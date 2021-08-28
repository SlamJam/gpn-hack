import json

import httpx
import luigi
import luigi.contrib.s3
import trio

from .. import hh, utils
from .common import BUCKET_NAME


def ids_s3_key_for_area(area_id):
    return f"s3://{BUCKET_NAME}/area_{area_id}_companies_ids.json"


def infos_s3_key_for_area(area_id):
    return f"s3://{BUCKET_NAME}/area_{area_id}_companies_info.json"


def cleared_infos_s3_key_for_area(area_id):
    return f"s3://{BUCKET_NAME}/area_{area_id}_companies_info_stripped.json"


def contries_s3_key():
    return f"s3://{BUCKET_NAME}/contries.json"


class HHScrapArea(luigi.Task):
    area_id = luigi.IntParameter()

    def run(self):
        data = trio.run(hh.collect_companies_ids_with_parsing, self.area_id)

        with self.output().open("w") as f:
            utils.save_pretty_json(sorted(data), f)

    def output(self):
        return luigi.contrib.s3.S3Target(ids_s3_key_for_area(self.area_id))


class HHResolveCompaniesAtArea(luigi.Task):
    area_id = luigi.IntParameter()

    def requires(self):
        return HHScrapArea(self.area_id)

    def run(self):
        with self.input().open() as f:
            data = json.load(f)

        res = trio.run(hh.resolve_companies_info, data)

        with self.output().open("w") as f:
            utils.save_pretty_json(res, f)

    def output(self):
        return luigi.contrib.s3.S3Target(infos_s3_key_for_area(self.area_id))


class HHClearCompaniesDescriptionsAtArea(luigi.Task):
    area_id = luigi.IntParameter()

    def requires(self):
        return HHResolveCompaniesAtArea(self.area_id)

    def run(self):
        with self.input().open() as f:
            data = json.load(f)

        with self.output().open("w") as f:
            utils.save_pretty_json([hh.strip_tags_in_description(c) for c in data], f)

    def output(self):
        return luigi.contrib.s3.S3Target(cleared_infos_s3_key_for_area(self.area_id))


class HHGetContries(luigi.Task):
    def run(self):
        data = trio.run(hh.get_contries, httpx.AsyncClient())

        with self.output().open("w") as f:
            utils.save_pretty_json(data, f)

    def output(self):
        return luigi.contrib.s3.S3Target(contries_s3_key())
