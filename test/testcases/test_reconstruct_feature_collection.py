import json
import unittest
from pathlib import Path

from common import get_server_url, send_get_request, send_post_request, setup_logger

# python3 -m unittest -vv test_reconstruct_feature_collection.py


class ReconstructPointsTestCase(unittest.TestCase):
    def setUp(self):
        pass

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
        cls.logger.debug("tearDownClass")

    def test_reconstruct_feature_collection(self):
        """-   testing {}/reconstruct/reconstruct_feature_collection/"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            params=self.data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)
        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"

        # TODO:
        self.data["keep_properties"] = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            params=self.data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)
        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"

        # TODO:
        r = send_post_request(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            data=self.data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)
        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"

        self.logger.info(
            "######### test_reconstruct_feature_collection ###########\n"
            + msg
            + "\n########## end of test_reconstruct_feature_collection ##########\n"
        )
