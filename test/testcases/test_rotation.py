import json
import logging
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


if __name__ == "__main__":
    unittest.main()
