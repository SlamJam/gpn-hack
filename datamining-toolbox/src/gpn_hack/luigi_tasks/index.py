import json

import elasticsearch as es
import luigi
import luigi.contrib.s3
import luigi.mock
import more_itertools as mit

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
        # FIXME: For debug only
        # with open("area_113_companies_info_stripped.json") as f:

        _, area_input = self.input()
        with area_input.open() as f:
            # data = ijson.items(f, "item")
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
                    meta = {"index": {}}
                    doc = {
                        "name": c["name"],
                        "email": "",
                        "phone": "",
                        "site_url": c["site_url"],
                        "description": c["description"],
                    }

                    yield meta
                    yield doc

            client = es.Elasticsearch(ELASTICSEARCH_URL)

            chunk_size = 1000
            for i, chunk in enumerate(mit.chunked(data, chunk_size)):
                print("Load chunk:", i, "docs:", i * chunk_size + len(chunk))

                body = "\n".join(map(json.dumps, company_docs_to_es_bulk(chunk)))
                res = client.bulk(index="companies", body=body)
                # print(res)

        with self.output().open("w"):
            pass

    def output(self):
        return luigi.mock.MockTarget(f"indexing/IndexHHArea{self.area_id}")


class IndexHH(luigi.Task):
    areas_ids = luigi.ListParameter(DEFAULT_HH_AREAS)

    def requires(self):
        return [IndexHHArea(area_id) for area_id in self.areas_ids]
