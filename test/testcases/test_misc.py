import json
import logging
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_misc.py

# pay attention here !!! this testcase can reveal some excessive memory usage issue.


class MiscTestCase(unittest.TestCase):
    SERVER_URL = ""
    logger = logging.getLogger()

    def setUp(self):
        self.proxies = {"http": ""}

    def tearDown(self):
        self.logger.info("tearDown")

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem, logging.INFO)
        get_server_url(cls)

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("tearDownClass")

    @add_server_url_to_docstring()
    def test_motion_path(self):
        """-   testing {}/reconstruct/motion_path?seedpoints=0,0&movplate=701"""

        data = {"seedpoints": "0,0", "movplate": 701}
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/motion_path",
            params=data,
        )
        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))
        self.assertEqual(r.status_code, 200)

        logging.info(
            "######### test_motion_path ###########\n"
            + json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            + "######### test_motion_path ###########\n"
        )

    @add_server_url_to_docstring()
    def test_find_axis_and_angle(self):
        """-   testing {}/earth/find_axis_and_angle?point_a=120,45&point_b=20,-45"""
        data = {"point_a": "120,45", "point_b": "20,-45"}
        r = send_get_request(
            self.SERVER_URL + "/earth/find_axis_and_angle",
            params=data,
        )
        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))
        self.assertEqual(r.status_code, 200)

        logging.info(
            "######### test_find_axis_and_angle ###########\n"
            + json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            + "######### test_find_axis_and_angle ###########\n"
        )

    @add_server_url_to_docstring()
    def test_interp_two_locations(self):
        """-   testing {}/earth/interp_two_locations?point_a=120,45&point_b=20,-45&num=10"""

        data = {"point_a": "120,45", "point_b": "20,-45", "num": 10}
        r = send_get_request(
            self.SERVER_URL + "/earth/interp_two_locations", params=data
        )
        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))
        self.assertEqual(r.status_code, 200)

        logging.info(
            "######### test_interp_two_locations ###########\n"
            + json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            + "\n########## end of test_interp_two_locations ##########\n"
        )

    @add_server_url_to_docstring()
    def test_distance(self):
        """-   testing {}/earth/distance?point_a=120,45&point_b=20,-45"""

        data = {"point_a": "120,45", "point_b": "20,-45"}
        r = send_get_request(self.SERVER_URL + "/earth/distance", params=data)
        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))
        self.assertEqual(r.status_code, 200)

        dist = json.loads(r.text)
        self.assertAlmostEqual(dist["distance"], 14018, delta=1)
        logging.info(
            "######### test_distance ###########\n"
            + json.dumps(dist, sort_keys=True, indent=4)
            + "\n########## end of test_distance ##########\n"
        )

    @add_server_url_to_docstring()
    def test_paleo_cities(self):
        """-   testing {}/earth/get_cities?time=100&model=muller2019"""

        r = send_get_request(
            self.SERVER_URL + "/earth/get_cities",
            params={"time": 100, "model": "muller2019"},
        )
        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))
        self.assertEqual(r.status_code, 200)

        return_data = json.loads(str(r.text))
        self.logger.info(
            "######### test_paleo_cities ###########\n"
            + json.dumps(return_data, sort_keys=True, indent=4)
            + "\n########## end of test_paleo_cities ##########\n"
        )

        self.assertEqual(len(return_data["names"]), len(return_data["lons"]))
        self.assertEqual(len(return_data["names"]), len(return_data["lats"]))

    @add_server_url_to_docstring()
    def test_get_present_day_cities(self):
        """-   testing {}/earth/get_present_day_cities"""

        r = send_get_request(
            self.SERVER_URL + "/earth/get_present_day_cities",
        )
        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))

        self.assertEqual(r.status_code, 200)

        self.logger.info(
            "######### test_get_present_day_cities ###########\n"
            + json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            + "\n########## end of test_get_present_day_cities ##########\n"
        )

    @add_server_url_to_docstring()
    def test_paleo_labels(self):
        """-   testing {}/earth/get_labels?time=300&model=merdith2021"""

        r = send_get_request(
            self.SERVER_URL + "/earth/get_labels",
            params={"time": 300, "model": "merdith2021"},
        )
        if r.request.url:
            self.logger.info(r.request.url + str(r.request.headers))

        self.assertEqual(r.status_code, 200)

        self.logger.info(
            "######### test_paleo_labels ###########\n"
            + json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            + "\n########## end of test_paleo_labels ##########\n"
        )


if __name__ == "__main__":
    unittest.main()
