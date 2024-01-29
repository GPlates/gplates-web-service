import json
import logging
import time
import unittest
from pathlib import Path

import requests
from common import get_server_url, setup_logger

# python3 -m unittest -vv test_misc.py


class MiscTestCase(unittest.TestCase):
    def setUp(self):
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

    def test_motion_path(self):
        """test motion path"""
        time.sleep(1)
        data = {"seedpoints": "0,0", "movplate": 701}
        r = requests.get(
            self.SERVER_URL + "/reconstruct/motion_path",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! test motion path")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_find_axis_and_angle(self):
        """test find_axis_and_angle"""
        time.sleep(1)
        data = {"point_a": "120,45", "point_b": "20,-45"}
        r = requests.get(
            self.SERVER_URL + "/earth/find_axis_and_angle",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! test find_axis_and_angle")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_interp_two_locations(self):
        """test interp_two_locations"""
        time.sleep(1)
        data = {"point_a": "120,45", "point_b": "20,-45", "num": 10}
        r = requests.get(
            self.SERVER_URL + "/earth/interp_two_locations",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! test interp_two_locations")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_distance(self):
        """test distance"""
        time.sleep(1)
        data = {"point_a": "120,45", "point_b": "20,-45"}
        r = requests.get(
            self.SERVER_URL + "/earth/distance",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! test distance")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_paleo_labels(self):
        """test paleo-labels"""
        time.sleep(1)
        data = {"time": 100, "model": "muller2019"}
        r = requests.get(
            self.SERVER_URL + "/earth/get_labels",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            self.logger.info(
                json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            )
            self.logger.info("PASSED! test_paleo_labels")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_paleo_cities_1(self):
        """test paleo-cities test_paleo_cities"""
        time.sleep(1)
        data = {"time": 100, "model": "muller2019"}
        r = requests.get(
            self.SERVER_URL + "/earth/get_cities",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            self.logger.info(
                json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            )
            self.logger.info("PASSED! test_paleo_cities")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_paleo_cities_2(self):
        """test paleo-cities get_present_day_cities"""
        time.sleep(1)
        r = requests.get(
            self.SERVER_URL + "/earth/get_present_day_cities",
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            self.logger.info(
                json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            )
            self.logger.info("PASSED! test_paleo_cities_2")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))


if __name__ == "__main__":
    unittest.main()
