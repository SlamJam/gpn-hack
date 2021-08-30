import itertools as it
import tempfile
import typing

import elastic_enterprise_search as ees
import elasticsearch as es
import elasticsearch.exceptions
import luigi
import luigi.contrib.s3
import luigi.format
import luigi.mock
import more_itertools as mit
import pydantic
from elasticsearch.client import CatClient
from elasticsearch.helpers import bulk

from .. import embedder, qdrant, utils
from . import hh
from .common import DEFAULT_HH_AREAS, ELASTICSEARCH_URL, QDRANT_URL

EES_ENGINE_NAME = "gazpromneft1"
EES_URL = "https://gazpromneft.ent.eastus2.azure.elastic-cloud.com"
EES_AUTH_KEY = "private-4xzeh815k7k5ffooxy4va621"
INDEX_EES = False


COMPANIES_COLLECTION = "companies"
QDRANT_COLLECTION = "companies"
FASTTEXT_MODEL_KEY = "s3://fasttext-model/ft_model_small.bin"
ENERGYBASE_DATA_KEY = "s3://energybase/result.jsonl.gz"


class PrepareEmbedderModel(luigi.Task):
    def output(self):
        return luigi.contrib.s3.S3Target(FASTTEXT_MODEL_KEY, format=luigi.format.Nop)


class PrepareEnergybaseData(luigi.Task):
    def output(self):
        return luigi.contrib.s3.S3Target(ENERGYBASE_DATA_KEY, format=luigi.format.Gzip)


class Company(pydantic.BaseModel):
    # id: int
    name: str
    description: typing.Optional[str] = None

    email: str = ""
    phone: str = ""
    site_url: str = ""

    industries: typing.List[str] = []

    # ---
    source: str


class IndexItem(pydantic.BaseModel):
    id: int
    company: Company
    descriptor: typing.Optional[typing.List[float]] = None  # np.ndarray
    similar_ids: typing.List[int] = []

    @property
    def qdrant_point(self):
        assert self.descriptor, "descriptor must be not None"
        return {"id": self.id, "vector": self.descriptor}

    @property
    def elastic_doc(self):
        doc = self.company.dict()
        doc["_id"] = self.id
        doc["similar_ids"] = self.similar_ids

        return doc


def iter_hh_area_data(f) -> typing.List[Company]:
    data = utils.iter_over_jsonl(f)

    # 47 - отрасль "Нефть и газ"
    data = filter(
        lambda c: any(
            ind_id == "47" or ind_id.startswith("47.") for ind in c["industries"] if (ind_id := ind["id"]) or True
        ),
        data,
    )

    def fix(c):
        c["source"] = "hh"

        c["industries"] = [ind["name"] for ind in c["industries"]]

        if c["site_url"] == "http://":
            c.pop("site_url")

        return c

    data = map(fix, data)

    return map(Company.parse_obj, data)


def iter_energybase_data(f) -> typing.List[Company]:
    data = utils.iter_over_jsonl(f)

    def fix(c):
        c["source"] = "energybase"

        attrs = c["attributes"]
        c["email"] = attrs["email"]
        c["phone"] = attrs["phone"]
        c["site_url"] = attrs["site"]

        return c

    data = map(fix, data)

    return map(Company.parse_obj, data)


def create_indexitem(ft_model, num: int, company: Company) -> IndexItem:
    descriptor = None

    if company.description:
        # TODO: split ',', '.', ' '
        descriptor = [float(num) for num in embedder.sema_embedder(company.description.split(), ft_model)]

    return IndexItem(id=num, company=company, descriptor=descriptor)


def index_es(es_client, chunk):
    bulk(client=es_client, index=COMPANIES_COLLECTION, actions=(c.elastic_doc for c in chunk))


def index_ees(ees_client, chunk):
    def fix(doc):
        # EES reject fields which start with "_"
        doc["id"] = doc.pop("_id")

        return doc

    ees_client.index_documents(
        engine_name=EES_ENGINE_NAME,
        documents=[fix(c.elastic_doc) for c in chunk],
    )


class IndexHHArea(luigi.Task):
    area_id = luigi.IntParameter()

    def requires(self):
        return PrepareEmbedderModel(), hh.HHClearCompaniesDescriptionsAtArea(self.area_id), PrepareEnergybaseData()

    def run(self):
        if INDEX_EES:
            ees_client = ees.AppSearch(EES_URL, http_auth=EES_AUTH_KEY)

            try:
                ees_client.get_engine(engine_name=EES_ENGINE_NAME)
                # ees_client.delete_engine(engine_name=EES_ENGINE_NAME)
            except ees.NotFoundError:
                pass
            else:
                print(f"Engine {EES_ENGINE_NAME} already exists. Nothing to do.")
                return
        else:
            es_client = es.Elasticsearch(ELASTICSEARCH_URL)
            es_cat_client = CatClient(es_client)

            # Check existing index
            try:
                es_cat_client.indices(index=COMPANIES_COLLECTION)
            except elasticsearch.exceptions.NotFoundError:
                pass
            else:
                print(f"Collection {COMPANIES_COLLECTION} already exists. Nothing to do.")
                self.mark_sucess()
                return

        fasttext_model, hh_area_input, energybase_input = self.input()

        # ===== Prepare Embedder =====

        # We neeeeed fileNAME, copy data to temporary file... with name
        with tempfile.NamedTemporaryFile() as f:
            with fasttext_model.open() as f_mdl:
                buf_size = 1 * 1024 * 1024
                while len(buf := f_mdl.read(buf_size)) != 0:
                    f.write(buf)
                f.seek(0)

            ft_model = embedder.load_gensim_model(f.name)

        # ===== Indexing Qdrant =====

        with hh_area_input.open() as hh_f, energybase_input.open() as eb_f:
            hh_data = iter_hh_area_data(hh_f)
            energybase_data = iter_energybase_data(eb_f)

            all_iter_data = it.chain(hh_data, energybase_data)

            index_data = [create_indexitem(ft_model, i + 1, c) for i, c in enumerate(all_iter_data)]

        print("Index items count:", len(index_data))

        # ===== Prepare Qdrant =====

        qdr = qdrant.QIndexer(url=QDRANT_URL)
        qdr.drop_collection(QDRANT_COLLECTION)
        qdr.create_collection(QDRANT_COLLECTION)

        # ===== Indexing Qdrant =====

        chunk_size = 1000
        for i, chunk in enumerate(mit.chunked(filter(lambda item: item.descriptor, index_data), chunk_size)):
            print("Qdrant | Load chunk:", i, "docs:", i * chunk_size + len(chunk))
            # print(chunk)
            qdr.bulk_load(QDRANT_COLLECTION, (c.qdrant_point for c in chunk))

        for item in index_data:
            if not item.descriptor:
                continue

            item.similar_ids = qdr.similar_topn(QDRANT_COLLECTION, item.descriptor, 5)

        # ===== Indexing Elastic =====

        if INDEX_EES:
            ees_client.create_engine(
                engine_name=EES_ENGINE_NAME,
                language="ru",
            )

        chunk_size = 100
        for i, chunk in enumerate(mit.chunked(index_data, chunk_size)):
            print("Elastic | Load chunk:", i, "docs:", i * chunk_size + len(chunk))

            if INDEX_EES:
                index_ees(ees_client, chunk)
            else:
                index_es(es_client, chunk)

        self.mark_sucess()

    def mark_sucess(self):
        with self.output().open("w"):
            pass

    def output(self):
        return luigi.mock.MockTarget(f"indexing/IndexHHArea{self.area_id}")


class IndexHH(luigi.Task):
    areas_ids = luigi.ListParameter(DEFAULT_HH_AREAS)

    def requires(self):
        return [IndexHHArea(area_id) for area_id in self.areas_ids]

    def run(self):
        with self.output().open("w"):
            pass

    def output(self):
        return luigi.mock.MockTarget("indexing/IndexHH")
