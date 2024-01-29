import json
import logging
import time
import unittest
from pathlib import Path

import requests
from common import get_server_url, setup_logger

# python3 -m unittest -vv test_raster_query.py


class RasterQueryCase(unittest.TestCase):
    def setUp(self):
        time.sleep(1)
        self.proxies = {"http": ""}

    def tearDown(self):
        self.logger.info("tearDown")

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("tearDownClass")

    def test_raster_query(self):
        # test raster query
        data = {"lon": 99.50, "lat": -40.24, "raster_name": "crustal_thickness"}
        r = requests.get(
            self.SERVER_URL + "/raster/query/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        if r.status_code == 200:
            logging.info(r.text)
            self.logger.info(f"PASSED! raster query ({r.text})")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_raster_query_multiple_locations_1(self):
        # test raster query multiple locations
        data = {
            "lons": json.dumps([99.50, 0, 10]),
            "lats": json.dumps([-40.24, 0, 20]),
            "raster_name": "crustal_thickness",
        }
        r = requests.get(
            self.SERVER_URL + "/raster/query/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        if r.status_code == 200:
            logging.info(r.text)
            self.logger.info(f"PASSED! raster query ({r.text})")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_raster_query_multiple_locations_2(self):
        # test raster query multiple locations
        data = {
            "lons": "99.50, 0, 10",
            "lats": "-40.24, 0, 20",
            "raster_name": "crustal_thickness",
        }
        r = requests.get(
            self.SERVER_URL + "/raster/query/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        if r.status_code == 200:
            logging.info(r.text)
            self.logger.info(f"PASSED! raster query ({r.text})")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_raster_query_multiple_locations_3(self):
        # test raster query multiple locations
        data = {
            "points": "99.50, -40.24, 0, 0, 10, 20",
            "raster_name": "crustal_thickness",
        }
        r = requests.get(
            self.SERVER_URL + "/raster/query/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        if r.status_code == 200:
            logging.info(r.text)
            self.logger.info(f"PASSED! raster query ({r.text})")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_list_raster_names(self):
        # test list raster names

        r = requests.get(
            self.SERVER_URL + "/raster/list/",
            verify=False,
            proxies=self.proxies,
        )
        if r.status_code == 200:
            logging.info(r.text)
            self.logger.info(f"PASSED! raster list name ({r.text})")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))


if __name__ == "__main__":
    unittest.main()
