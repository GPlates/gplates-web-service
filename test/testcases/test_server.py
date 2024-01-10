import json
import logging
import time
import unittest
from pathlib import Path

import common
import requests


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.proxies = {"http": ""}

    def tearDown(self):
        self.logger.info("tearDown")

    @classmethod
    def setUpClass(cls):
        common.setup_logger(cls, Path(__file__).stem)
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

    def test_reconstruct_points_get(self):
        """test GET reconstructing points"""
        time.sleep(1)
        data = {"points": "95,54,142,-33", "time": 140}
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! GET reconstruct points")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_reconstruct_points_post(self):
        """test POST reconstructing points"""
        time.sleep(1)
        data = {"points": "95,54,142,-33", "time": 140}
        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! POST reconstruct points")
        else:
            raise Exception(
                "FAILED: " + r.request.url + r.request.body + str(r.request.headers)
            )

    def test_reconstruct_points_post_fc(self):
        """test POST reconstructing points(return feature collection)"""
        time.sleep(1)
        data = {"points": "95,54,-117.26,32.7,142,-33", "time": 140, "fc": ""}
        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info(
                "PASSED! POST reconstruct points(return feature collection)"
            )
        else:
            raise Exception(
                "FAILED: " + r.request.url + r.request.body + str(r.request.headers)
            )

    def test_reconstruct_points_get_fc(self):
        """test GET reconstructing points(return feature collection)"""
        time.sleep(1)
        data = {"points": "95,54,-117.26,32.7,142,-33", "time": 140, "fc": ""}
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info(
                "PASSED! GET reconstruct points(return feature collection)"
            )
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

        # test raster query
        data = {"lon": 99.50, "lat": -40.24, "raster_name": "age_grid_geek_2007"}
        r = requests.get(
            self.SERVER_URL + "/raster/query/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        if r.status_code == 200:
            logging.info(r.text)
            self.logger.info(f"PASSED! raster query ({r.text})")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

    def test_reconstruct_feature_collection(self):
        """test reconstruct feature collection"""
        time.sleep(1)
        data = {"feature_collection": json.dumps(self.fc), "time": 140}
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        if r.status_code == 200:
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! test reconstruct feature collection")
        else:
            raise Exception("FAILED: " + r.request.url + str(r.request.headers))

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
            logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
            self.logger.info("PASSED! test rotate")
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


if __name__ == "__main__":
    unittest.main()
