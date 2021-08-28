import json

import luigi
import luigi.contrib.s3
import luigi.mock
import manticoresearch
import more_itertools as mit

from . import hh
from .common import DEFAULT_HH_AREAS, MANTICORE_URL


# Defining the host is optional and defaults to http://127.0.0.1:9308
# See configuration.py for a list of all supported configuration parameters.
configuration = manticoresearch.Configuration(host=MANTICORE_URL)


class InitIndex(luigi.Task):
    def run(self):
        with manticoresearch.ApiClient(configuration) as api_client:
            # creating table
            api_instance = manticoresearch.UtilsApi(api_client)

            res = api_instance.sql(
                "mode=raw&query=CREATE TABLE if not exists companies"
                "("
                "name text stored indexed, "
                "email text stored indexed, "
                "site_url text stored, "
                "phone text, "
                "description text stored indexed, "
                "name_morph text indexed, "
                "description_morph text indexed"
                ") "
                "min_prefix_len = '3' "
                "morphology = 'stem_ru' "
                "stopwords = 'ru' "
                "morphology_skip_fields = 'name,phone,email,description, site_url' "
            )
            print(res)

            # res = api_instance.sql('mode=raw&query=SHOW TABLES')
            # print(res)

        with self.output().open('w'):
            pass

    def output(self):
        return luigi.mock.MockTarget("indexing/InitIndex")


class IndexHHArea(luigi.Task):
    area_id = luigi.IntParameter()

    def requires(self):
        return InitIndex(), hh.HHClearCompaniesDescriptionsAtArea(self.area_id)

    def run(self):
        with manticoresearch.ApiClient(configuration) as api_client:
            # bulk index method
            api_instance = manticoresearch.IndexApi(api_client)

            print("Load data")

            _, area_input = self.input()
            with area_input.open() as f:
                data = json.load(f)

            print("Start indexing")

            # 47 - отрасль "Нефть и газ"
            data = filter(lambda c: any(ind == "47" or ind.startswith("47.") for ind in c["industries"]), data)

            chunk_size = 1000
            for i, chunk in enumerate(mit.chunked(data, chunk_size)):
                print("Load chunk:", i, "docs:", i * chunk_size + len(chunk))
                docs = [
                    {
                        "insert": {
                            "index": "companies",
                            "doc": {
                                "name": c["name"],
                                "name_morph": c["name"],
                                "email": "",
                                "phone": "",
                                "site_url": c["site_url"],
                                "description": c["description"],
                                "description_morph": c["description"],
                            },
                        }
                    }
                    for c in chunk
                ]

                res = api_instance.bulk("\n".join(map(json.dumps, docs)))
                # print(res)

            with self.output().open('w'):
                pass

    def output(self):
        return luigi.mock.MockTarget(f"indexing/IndexHHArea{self.area_id}")


class IndexHH(luigi.Task):
    areas_ids = luigi.ListParameter(DEFAULT_HH_AREAS)

    def requires(self):
        return [IndexHHArea(area_id) for area_id in self.areas_ids]
