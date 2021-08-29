import tempfile

import elasticsearch as es
import elasticsearch.exceptions
import luigi
import luigi.contrib.s3
import luigi.format
import luigi.mock
import more_itertools as mit
from elastic_enterprise_search import AppSearch
from elasticsearch.client import CatClient
from elasticsearch.helpers import bulk

from .. import embedder, qdrant, utils
from . import hh
from .common import DEFAULT_HH_AREAS, ELASTICSEARCH_URL, QDRANT_URL

EES_ENGINE_NAME = "gazpromneft"
EES_URL = "https://gazpromneft.ent.eastus2.azure.elastic-cloud.com"
EES_AUTH_KEY = "private-4xzeh815k7k5ffooxy4va621"


COMPANIES_COLLECTION = "companies"
QDRANT_COLLECTION = "companies"
FASTTEXT_MODEL_KEY = "s3://fasttext-model/ft_model_small.bin"


class PrepareEmbedderModel(luigi.Task):
    def output(self):
        return luigi.contrib.s3.S3Target(FASTTEXT_MODEL_KEY, format=luigi.format.Nop)


def iter_over_gas_oil(f):
    data = utils.iter_over_jsonl(f)

    # 47 - отрасль "Нефть и газ"
    yield from filter(
        lambda c: any(
            ind_id == "47" or ind_id.startswith("47.") for ind in c["industries"] if (ind_id := ind["id"]) or True
        ),
        data,
    )


class IndexHHArea(luigi.Task):
    area_id = luigi.IntParameter()

    def requires(self):
        return PrepareEmbedderModel(), hh.HHClearCompaniesDescriptionsAtArea(self.area_id)

    def run(self):
        es_client = es.Elasticsearch(ELASTICSEARCH_URL)
        es_cat_client = CatClient(es_client)

        ees_client = AppSearch(EES_URL, http_auth=EES_AUTH_KEY)

        # Check existing index
        # try:
        #     es_cat_client.indices(index=COMPANIES_COLLECTION)
        # except elasticsearch.exceptions.NotFoundError:
        #     pass
        # else:
        #     print(f"Collection {COMPANIES_COLLECTION} already exists. Nothing to do.")
        #     self.mark_sucess()
        #     return

        fasttext_model, area_input = self.input()

        # # Prepare Embedder

        # # We neeeeed fileNAME, copy data to temporary file... with name
        # with tempfile.NamedTemporaryFile() as f:
        #     with fasttext_model.open() as f_mdl:
        #         buf_size = 1 * 1024 * 1024
        #         while len(buf := f_mdl.read(buf_size)) != 0:
        #             f.write(buf)
        #         f.seek(0)

        #     ft_model = embedder.load_gensim_model(f.name)

        # # Prepare Qdrant
        # qdr = qdrant.QIndexer(url=QDRANT_URL)
        # qdr.drop_collection(QDRANT_COLLECTION)
        # qdr.create_collection(QDRANT_COLLECTION)

        # # Indexing Qdrant
        # with area_input.open() as f:
        #     data = iter_over_gas_oil(f)

        #     def company_to_qdrant_point(doc):
        #         desc = doc.get("description") or "нет описания"

        #         # TODO: split ',', '.', ' '
        #         descriptor = embedder.sema_embedder(desc.split(), ft_model)
        #         return {"id": doc["id"], "vector": [float(num) for num in descriptor]}

        #     chunk_size = 1
        #     for i, chunk in enumerate(mit.chunked(map(company_to_qdrant_point, data), chunk_size)):
        #         print("Qdrant | Load chunk:", i, "docs:", i * chunk_size + len(chunk))
        #         print(chunk)
        #         qdr.bulk_load(QDRANT_COLLECTION, chunk)

        # Indexing Elastic

        with area_input.open() as f:
            data = iter_over_gas_oil(f)

            def company_to_es_doc(c):
                return {
                    # EES reject fields which start with "_"
                    # "_id": c["id"],
                    "id": c["id"],
                    "name": c["name"],
                    "email": "",
                    "phone": "",
                    "site_url": c["site_url"],
                    "description": c["description"],
                    "industries": [ind["name"] for ind in c.get("industries", [])],
                }

            chunk_size = 100
            for i, chunk in enumerate(mit.chunked(map(company_to_es_doc, data), chunk_size)):
                print("Elastic | Load chunk:", i, "docs:", i * chunk_size + len(chunk))
                # bulk(client=es_client, index="companies", actions=chunk)
                ees_client.index_documents(
                    engine_name=EES_ENGINE_NAME,
                    documents=chunk,
                )

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
