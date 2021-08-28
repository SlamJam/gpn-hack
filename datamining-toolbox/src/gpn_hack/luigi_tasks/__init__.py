import logging

import luigi
import luigi.contrib.s3

from . import hh

# Disable all child loggers
logging.getLogger("botocore").propagate = False
logging.getLogger("boto3").propagate = False


class MainTask(luigi.Task):
    # 113 - Россия, 1 - Москва, 83 - Смоленск
    # areas_ids = luigi.ListParameter([113])
    areas_ids = luigi.ListParameter([113])

    def requires(self):
        return [hh.HHClearCompaniesDescriptionsAtArea(area_id) for area_id in self.areas_ids] + [hh.HHGetContries()]
