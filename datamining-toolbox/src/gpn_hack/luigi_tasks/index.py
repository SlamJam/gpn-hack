import elasticsearch as es
import elasticsearch.exceptions
import luigi
import luigi.contrib.s3
import luigi.mock
import more_itertools as mit
from elasticsearch.client import CatClient
from elasticsearch.helpers import bulk

from .. import utils
from . import hh
from .common import DEFAULT_HH_AREAS, ELASTICSEARCH_URL

COMPANIES_COLLECTION = "companies"


class InitIndex(luigi.Task):
    def run(self):
        # TODO: recreate collection in ES
        pass

        with self.output().open("w"):
            pass

    def output(self):
        return luigi.mock.MockTarget("indexing/InitIndex")


class IndexHHArea(luigi.Task):
    area_id = luigi.IntParameter()

    def requires(self):
        return InitIndex(), hh.HHClearCompaniesDescriptionsAtArea(self.area_id)

    def run(self):
        _, area_input = self.input()
        with area_input.open() as f:
            data = utils.iter_over_jsonl(f)

            # 47 - отрасль "Нефть и газ"
            data = filter(
                lambda c: any(
                    ind_id == "47" or ind_id.startswith("47.")
                    for ind in c["industries"]
                    if (ind_id := ind["id"]) or True
                ),
                data,
            )

            def company_docs_to_es_bulk(companies):
                for c in companies:
                    yield {
                        "_id": "hh_" + c["id"],
                        "name": c["name"],
                        "email": "",
                        "phone": "",
                        "site_url": c["site_url"],
                        "description": c["description"],
                    }

            client = es.Elasticsearch(ELASTICSEARCH_URL)
            cat_client = CatClient(client)

            try:
                cat_client.indices(index=COMPANIES_COLLECTION)
            except elasticsearch.exceptions.NotFoundError:
                pass
            else:
                print(f"Collection {COMPANIES_COLLECTION} already exists. Nothing to do.")
                self.mark_sucess()
                return

            chunk_size = 1000
            for i, chunk in enumerate(mit.chunked(data, chunk_size)):
                print("Load chunk:", i, "docs:", i * chunk_size + len(chunk))
                bulk(client=client, index="companies", actions=company_docs_to_es_bulk(chunk))

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
