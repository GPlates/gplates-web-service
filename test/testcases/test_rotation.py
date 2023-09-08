import json
import logging
import random
import os
import unittest
from pathlib import Path

import requests
import urllib3


class RotationTestCase(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger()
        Path("logs").mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler("logs/test-rotation.log")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s \n\n%(message)s\n")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # print(self.logger.handlers)
        urllib3.disable_warnings()

        self.SERVER_URL = os.getenv("GWS_SERVER_URL")
        if not self.SERVER_URL:
            self.SERVER_URL = "http://127.0.0.1:18000"
            self.logger.info(f"Using server URL in script {self.SERVER_URL}")
        else:
            self.logger.info(
                f"Using server URL in environment variable {self.SERVER_URL}"
            )

        self.proxies = {"http": ""}

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
