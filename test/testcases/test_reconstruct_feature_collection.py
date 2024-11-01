import json
import time
import unittest
from pathlib import Path

import requests
from common import get_server_url, setup_logger

# python3 -m unittest -vv test_reconstruct_feature_collection.py


class ReconstructPointsTestCase(unittest.TestCase):
    def setUp(self):
        self.proxies = {"http": ""}

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)
        cls.proxies = {"http": ""}
        feature_collection_data = {
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
                    "properties": {"id": 123, "test_property": 345},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [51.0, 38.0]},
                    "properties": {"id": 222},
                },
            ],
        }

        cls.data = {
            "feature_collection": json.dumps(feature_collection_data),
            "geologicage": 140,
            "model": "muller2019",
        }

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("tearDownClass")

    def test_reconstruct_feature_collection(self):
        # time.sleep(1)
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            params=self.data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))

        self.data["keep_properties"] = ""
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            params=self.data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))

        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            data=self.data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
