import json
import random
import time
import unittest
from pathlib import Path

import requests
from common import get_server_url, setup_logger

# python3 -m unittest -vv test_rotation.py


class RotationTestCase(unittest.TestCase):
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

    def test_rotate(self):
        """test rotate"""
        time.sleep(1)
        data = {"point": "120,45", "axis": "20,-45", "angle": 20}
        r = requests.get(
            self.SERVER_URL + "/rotation/rotate",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            self.logger.info(
                json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            )
            self.logger.info("PASSED! test rotate")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_get_plate_ids(self):
        """https://gws.gplates.org/rotation/get_plate_ids?time=100
        http://localhost/rotation/get_plate_ids?time=100
        """
        r = requests.get(
            self.SERVER_URL + "/rotation/get_plate_ids?time=100",
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(r.request.url + str(r.request.headers))

        self.assertEqual(r.status_code, 200)

        pids = json.loads(str(r.text))
        self.assertTrue(len(pids) > 0)

        self.logger.info(json.dumps(pids, sort_keys=True, indent=4))
        self.logger.info("PASSED! GET get_plate_ids")

    def test_finite_rotation(self):
        time = 100.0

        # get all the plate IDs in the reconstruction tree at 100Ma
        url = f"{self.SERVER_URL}/rotation/get_plate_ids?time=100"
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        pids = json.loads(r.text)
        self.logger.info(r.text)

        # pick up a random plate ID from above plate IDs
        random_pid = pids[random.randint(0, len(pids) - 1)]
        # print(random_pid)

        # rotate with euler pole and angle
        url = f"{self.SERVER_URL}/rotation/get_euler_pole_and_angle?times={time}&pids={random_pid}"
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.logger.info(r.text)

        # rotate with quaternions
        url = (
            f"{self.SERVER_URL}/rotation/get_quaternions?times={time}&pids={random_pid}"
        )
        # print(url)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.logger.info(r.text)

    def test_rotation_map(self):
        data = {"point": "120,45", "axis": "20,-45", "angle": 20}
        r = requests.get(
            self.SERVER_URL + "/rotation/rotate",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)

        r = requests.get(
            self.SERVER_URL + "/rotation/get_rotation_map/?model=MERDITH2021",
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        self.logger.info(r.text)

    def test_reconstruction_tree(self):
        r = requests.get(
            self.SERVER_URL
            + "/rotation/get_reconstruction_tree_edges/?model=seton2012&level=4&pids=707,702,314,833",
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)

        r = requests.get(
            self.SERVER_URL + "/rotation/get_reconstruction_tree_height",
            verify=False,
            proxies=self.proxies,
        )
        # print(r.text)
        self.assertEqual(r.status_code, 200)
        self.logger.info(r.text)

        r = requests.get(
            self.SERVER_URL + "/rotation/get_reconstruction_tree_leaves",
            verify=False,
            proxies=self.proxies,
        )
        # print(r.text)
        self.assertEqual(r.status_code, 200)
        self.logger.info(r.text)

        pids = json.loads(r.text)
        for pid in pids[:5]:
            r = requests.get(
                self.SERVER_URL
                + f"/rotation/get_ancestors_in_reconstruction_tree/?pid={pid}",
                verify=False,
                proxies=self.proxies,
            )
            self.assertEqual(r.status_code, 200)
            self.logger.info(r.text)


if __name__ == "__main__":
    unittest.main()
