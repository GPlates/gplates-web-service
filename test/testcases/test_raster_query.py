#!/usr/bin/env python3
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
        self.logger.info(
            f"test_raster_query: {r.text} {r.request.url} {str(r.request.headers)}"
        )
        self.assertEqual(r.status_code, 200)

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
        self.logger.info(
            f"test_raster_query_multiple_locations_1: {r.text} {r.request.url} {str(r.request.headers)}"
        )
        self.assertEqual(r.status_code, 200)

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
        self.logger.info(
            f"test_raster_query_multiple_locations_2: {r.text} {r.request.url} {str(r.request.headers)}"
        )
        self.assertEqual(r.status_code, 200)

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
        self.logger.info(
            f"test_raster_query_multiple_locations_3: {r.text} {r.request.url} {str(r.request.headers)}"
        )
        self.assertEqual(r.status_code, 200)

    def test_raster_query_multiple_locations_4(self):
        # test raster query multiple locations
        data = {
            "points": "[[99.50, -40.24], [0, 0], [10, 20]]",
            "raster_name": "crustal_thickness",
        }
        r = requests.get(
            self.SERVER_URL + "/raster/query/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(
            f"test_raster_query_multiple_locations_4: {r.text} {r.request.url} {str(r.request.headers)}"
        )
        self.assertEqual(r.status_code, 200)

    def test_raster_query_multiple_locations_5(self):
        # test raster query multiple locations
        data = {
            "points": "[[99aa.50, -40.24], [0, 0], [10, 20]]",
            "raster_name": "crustal_thickness",
        }
        r = requests.get(
            self.SERVER_URL + "/raster/query/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(
            f"test_raster_query_multiple_locations_5: {r.text} {r.request.url} {str(r.request.headers)}"
        )
        self.assertEqual(r.status_code, 400)

    def test_list_raster_names(self):
        # test list raster names

        r = requests.get(
            self.SERVER_URL + "/raster/list/",
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(
            f"test_list_raster_names: {r.text} {r.request.url} {str(r.request.headers)}"
        )
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
