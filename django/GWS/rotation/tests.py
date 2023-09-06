import json
import logging
import os

import requests
import urllib3
from django.test import TestCase

# this kind of test client is no good to be put here
# check out the test folder in code repository root
# keep these code here for future reference only

logging.basicConfig(filename="test.log", level=logging.INFO)

urllib3.disable_warnings()

SERVER_URL = os.getenv("GWS_SERVER_URL")
if not SERVER_URL:
    SERVER_URL = "http://127.0.0.1:80"
    print(f"Using server URL in script {SERVER_URL}")
else:
    print(f"Using server URL in environment variable {SERVER_URL}")

proxies = {"http": ""}


class RotationTestCase(TestCase):
    def setUp(self):
        print("setting up RotationTestCase")

    def test_get_plate_ids(self):
        """https://gws.gplates.org/rotation/get_plate_ids?time=100
        http://localhost/rotation/get_plate_ids?time=100
        """
        r = requests.get(
            SERVER_URL + "/rotation/get_plate_ids?time=100",
            verify=False,
            proxies=proxies,
        )
        logging.info(r.request.url + str(r.request.headers))

        self.assertEqual(r.status_code, 200)

        logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        print("PASSED! GET reconstruct points")
