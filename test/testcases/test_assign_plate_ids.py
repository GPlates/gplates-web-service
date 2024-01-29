import json
import logging
import time
import unittest
from pathlib import Path

import requests
from common import get_server_url, setup_logger

# python3 -m unittest -vv test_assign_plate_ids.py


class AssignPlateIDsTestCase(unittest.TestCase):
    def setUp(self):
        self.proxies = {"http": ""}

    def tearDown(self):
        self.logger.info("tearDown")

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)
        cls.fc = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [128, -17],
                                [133, -18],
                                [138, -19],
                                [140, -23],
                                [139, -27],
                                [130, -27],
                                [128, -24],
                                [127, -21],
                                [127, -17],
                                [128, -17],
                            ]
                        ],
                    },
                    "properties": {},
                }
            ],
        }

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("tearDownClass")

    def test_assign_plate_ids(self):
        """test assign plate ids for points"""
        time.sleep(1)
        data = {"points": "-10,50,-30,-70,0,0"}
        r = requests.get(
            self.SERVER_URL + "/reconstruct/assign_points_plate_ids",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! test assign plate ids for points")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_assign_plate_ids_geojson(self):
        """test assign plate ids for geojson data"""
        time.sleep(1)
        data = {"feature_collection": json.dumps(self.fc)}
        r = requests.get(
            self.SERVER_URL + "/reconstruct/assign_geojson_plate_ids",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! test assign plate ids for geojson data")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))


if __name__ == "__main__":
    unittest.main()
