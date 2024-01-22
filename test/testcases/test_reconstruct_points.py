import json
import random
import time
import unittest
from pathlib import Path

import requests
from common import get_server_url, setup_logger

# python3 -m unittest -vv test_reconstruct_points.py


class ReconstructPointsTestCase(unittest.TestCase):
    def setUp(self):
        time.sleep(1)

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)
        cls.proxies = {"http": ""}
        cls.data_1 = {"points": "95, 54, 142, -33", "time": 140}
        cls.data_2 = {"lons": "95, -117.26, 142", "lats": "54, 32.7, -33", "time": 140}
        cls.data_3 = {
            "lons": "95, -117.26, 142",
            "lats": "54, 32.7, -33",
            "times": "140, 100, 50",
        }

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("tearDownClass")

    def test_basic_get(self):
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=self.data_1,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_basic_post(self):
        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=self.data_1,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_post_return_feature_collection(self):
        data = self.data_2
        data["fc"] = True
        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_get_return_feature_collection(self):
        data = self.data_2
        data["fc"] = True
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_get_multi_times(self):
        data = self.data_3
        data["fc"] = False
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_post_multi_times(self):
        data = self.data_3
        data["fc"] = True
        self.logger.info(data)
        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(r.text)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
