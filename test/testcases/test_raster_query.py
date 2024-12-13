#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    get_test_flag,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_raster_query.py


@unittest.skipIf(
    get_test_flag("GWS_TEST_DB_QUERY") is not True,
    "GWS_TEST_DB_QUERY environment variable is not set to true.",
)
class RasterQueryCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        self.logger.debug("tearDown")

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)

    @classmethod
    def tearDownClass(cls):
        cls.logger.debug("tearDownClass")

    @add_server_url_to_docstring()
    def test_raster_query(self):
        """-   testing {}/raster/query/?lon=99.50&lat=-40.24&raster_name=crustal_thickness"""
        msg = ""
        data = {"lon": 99.50, "lat": -40.24, "raster_name": "crustal_thickness"}
        r = send_get_request(
            self.SERVER_URL + "/raster/query/",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_raster_query ###########\n\n"
            + msg
            + "\n########## end of test_raster_query ##########\n"
        )

    def test_raster_query_multiple_locations_1(self):
        """-   testing {}/raster/query/   (with multiple locations "lons": json.dumps([99.50, 0, 10]),"lats": json.dumps([-40.24, 0, 20])"""
        msg = ""
        data = {
            "lons": json.dumps([99.50, 0, 10]),
            "lats": json.dumps([-40.24, 0, 20]),
            "raster_name": "crustal_thickness",
        }
        r = send_get_request(
            self.SERVER_URL + "/raster/query/",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_raster_query_multiple_locations_1 ###########\n\n"
            + msg
            + "\n########## end of test_raster_query_multiple_locations_1 ##########\n"
        )

    def test_raster_query_multiple_locations_2(self):
        """-   testing {}/raster/query/   (with multiple locations "lons": "99.50, 0, 10", "lats": "-40.24, 0, 20",)"""
        msg = ""
        data = {
            "lons": "99.50, 0, 10",
            "lats": "-40.24, 0, 20",
            "raster_name": "crustal_thickness",
        }
        r = send_get_request(
            self.SERVER_URL + "/raster/query/",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_raster_query_multiple_locations_2 ###########\n\n"
            + msg
            + "\n########## end of test_raster_query_multiple_locations_2 ##########\n"
        )

    def test_raster_query_multiple_locations_3(self):
        """-   testing {}/raster/query/   (with multiple locations "points": "99.50, -40.24, 0, 0, 10, 20")"""
        msg = ""
        data = {
            "points": "99.50, -40.24, 0, 0, 10, 20",
            "raster_name": "crustal_thickness",
        }
        r = send_get_request(
            self.SERVER_URL + "/raster/query/",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_raster_query_multiple_locations_3 ###########\n\n"
            + msg
            + "\n########## end of test_raster_query_multiple_locations_3 ##########\n"
        )

    def test_raster_query_multiple_locations_4(self):
        """-   testing {}/raster/query/   (with multiple locations "points": "[[99.50, -40.24], [0, 0], [10, 20]]" """
        msg = ""
        data = {
            "points": "[[99.50, -40.24], [0, 0], [10, 20]]",
            "raster_name": "crustal_thickness",
        }
        r = send_get_request(
            self.SERVER_URL + "/raster/query/",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_raster_query_multiple_locations_4 ###########\n\n"
            + msg
            + "\n########## end of test_raster_query_multiple_locations_4 ##########\n"
        )

    def test_raster_query_multiple_locations_5(self):
        """-   testing {}/raster/query/   (with invalid location "points": "[[99aa.50, -40.24], [0, 0], [10, 20]]" """
        msg = ""
        data = {
            "points": "[[99aa.50, -40.24], [0, 0], [10, 20]]",
            "raster_name": "crustal_thickness",
        }
        r = send_get_request(
            self.SERVER_URL + "/raster/query/",
            params=data,
        )

        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        msg += r.text + "\n"
        self.logger.info(
            "######### test_raster_query_multiple_locations_5 ###########\n\n"
            + msg
            + "\n########## end of test_raster_query_multiple_locations_5 ##########\n"
        )
        self.assertEqual(r.status_code, 400)

    def test_list_raster_names(self):
        """-   testing {}/raster/list/"""
        msg = ""

        r = send_get_request(
            self.SERVER_URL + "/raster/list/",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_list_raster_names ###########\n\n"
            + msg
            + "\n########## end of test_list_raster_names ##########\n"
        )


if __name__ == "__main__":
    unittest.main()
