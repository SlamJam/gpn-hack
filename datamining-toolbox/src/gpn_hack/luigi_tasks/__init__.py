import logging

import luigi
import luigi.contrib.s3

from . import hh, index

# Disable all child loggers
for name in ["botocore", "boto3", "elasticsearch"]:
    logging.getLogger(name).propagate = False


class MainTask(luigi.Task):
    # 113 - Россия, 1 - Москва, 83 - Смоленск
    # areas_ids = luigi.ListParameter([113])
    areas_ids = luigi.ListParameter([113])

    def requires(self):
        return (
            [hh.HHClearCompaniesDescriptionsAtArea(area_id) for area_id in self.areas_ids]
            + [hh.HHGetContries()]
            + [index.IndexHH()]
        )
