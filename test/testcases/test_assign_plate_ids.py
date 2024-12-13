import json
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_assign_plate_ids.py


class AssignPlateIDsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        self.logger.debug("tearDown")

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
        cls.logger.debug("tearDownClass")

    @add_server_url_to_docstring()
    def test_assign_plate_ids(self):
        """-   testing {}/reconstruct/assign_points_plate_ids
        test assign plate ids for points"""
        msg = ""
        data = {"points": "-10, 50, -30, -70, 0, 0"}
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/assign_points_plate_ids",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"
        self.logger.info(
            "######### test_assign_plate_ids ###########\n\n"
            + msg
            + "\n########## end of test_assign_plate_ids ##########\n"
        )

    @add_server_url_to_docstring()
    def test_assign_plate_ids_geojson(self):
        """-   testing {}/reconstruct/assign_geojson_plate_ids
        test assigning plate ID for the polygon in geojson format
        """
        msg = ""
        data = {"feature_collection": json.dumps(self.fc)}
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/assign_geojson_plate_ids",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        ret_json_data = json.loads(str(r.text))
        msg += json.dumps(ret_json_data, sort_keys=True, indent=4) + "\n"
        self.assertEqual(len(ret_json_data), 1)  # only 1 plate ID being returned
        self.assertEqual(ret_json_data[0], 801)  # the plate ID should be 801

        self.logger.info(
            "######### test_assign_plate_ids_geojson ###########\n\n"
            + msg
            + "\n########## end of test_assign_plate_ids_geojson ##########\n"
        )


if __name__ == "__main__":
    unittest.main()
