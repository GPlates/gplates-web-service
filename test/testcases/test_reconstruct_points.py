import copy
import json
import math
import time
import unittest
from pathlib import Path

import pygplates
import requests
from common import get_server_url, setup_logger
from plate_model_manager import PlateModelManager

# python3 -m unittest -vv test_reconstruct_points.py


class ReconstructPointsTestCase(unittest.TestCase):
    def setUp(self):
        time.sleep(1)

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)
        cls.proxies = {"http": ""}
        cls.data_1 = {"points": "95, 54, 142, -33", "time": 140, "model": "Muller2019"}
        cls.data_2 = {"lons": "95, -117.26, 142", "lats": "54, 32.7, -33", "time": 140}
        cls.data_3 = {
            "lons": "95, -117.26, 142",
            "lats": "54, 32.7, -33",
            "times": "140, 100, 50",
            "model": "Muller2019",
        }
        cls.data_4 = {
            "lats": "50, 10, 50",
            "lons": "-100, 160, 100",
            "time": "100",
            "model": "PALEOMAP",
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

        try:
            gws_return_data = json.loads(str(r.text))
            self.logger.info(
                json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)
            )
        except Exception as e:
            self.logger.info(r.text)
            raise e
        self.assertEqual(r.status_code, 200)

        ps = self.data_1["points"].split(",")
        lats = ps[1::2]
        lons = ps[0::2]
        rlons, rlats = _reconstruct(
            lons, lats, self.data_1["model"], self.data_1["time"]
        )
        for i in range(len(rlons)):
            self.logger.info(f"{gws_return_data['coordinates'][int(i)][0]}, {rlons[i]}")
            self.logger.info(f"{gws_return_data['coordinates'][int(i)][1]}, {rlats[i]}")
            self.assertTrue(
                math.isclose(
                    gws_return_data["coordinates"][int(i)][0], rlons[i], abs_tol=0.0001
                )
            )
            self.assertTrue(
                math.isclose(
                    gws_return_data["coordinates"][int(i)][1], rlats[i], abs_tol=0.0001
                )
            )

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
        data = copy.copy(self.data_2)
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
        data = copy.copy(self.data_2)
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
        """test reconstruct points at multiple times
        use pygplates to verify the results
        """
        data = copy.copy(self.data_3)
        data["fc"] = False
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        try:
            gws_return_data = json.loads(str(r.text))
            self.logger.info(json.dumps(gws_return_data, sort_keys=True, indent=4))
        except Exception as e:
            self.logger.info(r.text)
            raise e
        self.assertEqual(r.status_code, 200)

        for time in self.data_3["times"].split(","):
            rlons, rlats = _reconstruct(
                self.data_3["lons"].split(","),
                self.data_3["lats"].split(","),
                self.data_3["model"],
                float(time),
            )
            for i in range(len(rlons)):
                rlon = 999.99 if rlons[i] is None else rlons[i]
                rlat = 999.99 if rlats[i] is None else rlats[i]

                self.assertTrue(
                    math.isclose(
                        gws_return_data[time.strip()]["coordinates"][int(i)][0],
                        rlon,
                        abs_tol=0.0001,
                    )
                )
                self.assertTrue(
                    math.isclose(
                        gws_return_data[time.strip()]["coordinates"][int(i)][1],
                        rlat,
                        abs_tol=0.0001,
                    )
                )

    def test_post_multi_times(self):
        data = copy.copy(self.data_3)
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

    def test_get_with_pid(self):
        data = copy.copy(self.data_1)
        data["pid"] = 701
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_get_with_pids(self):
        data = copy.copy(self.data_1)
        data["pids"] = "701, 801"
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=self.data_1,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(r.text)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_get_ignore_valid_time(self):
        data = copy.copy(self.data_2)
        data["ignore_valid_time"] = True
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=self.data_1,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(r.text)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_get_ignore_valid_time(self):
        data = copy.copy(self.data_4)
        data["ignore_valid_time"] = True

        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(r.text)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_get_return_null_points(self):
        data = copy.copy(self.data_4)
        data["return_null_points"] = True

        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(r.text)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_get_reverse(self):
        data = copy.copy(self.data_2)
        data["reverse"] = True

        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(r.text)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

    def test_get_simple_return_data(self):
        data = copy.copy(self.data_3)
        data["fmt"] = "simple"

        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info("test_get_simple_return_data: " + r.text)
        gws_return_data = json.loads(str(r.text))
        self.logger.info(json.dumps(gws_return_data, sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            len(data["times"].split(",")), len(list(gws_return_data.keys()))
        )
        for key in gws_return_data:
            self.assertEqual(
                len(data["lons"].split(",")), len(gws_return_data[key]["lons"])
            )
            self.assertEqual(
                len(data["lons"].split(",")), len(gws_return_data[key]["lats"])
            )
            self.assertEqual(
                len(data["lons"].split(",")), len(gws_return_data[key]["pids"])
            )
            self.assertEqual(
                len(data["lons"].split(",")), len(gws_return_data[key]["begin_time"])
            )
            self.assertEqual(
                len(data["lons"].split(",")), len(gws_return_data[key]["end_time"])
            )


def _reconstruct(lons, lats, model, time):
    point_features = []
    p_index = 0
    for lat, lon in zip(lats, lons):
        point_feature = pygplates.Feature()
        point_feature.set_geometry(pygplates.PointOnSphere(float(lat), float(lon)))
        point_feature.set_name(str(p_index))
        point_features.append(point_feature)
        p_index += 1

    properties_to_copy = [pygplates.PartitionProperty.reconstruction_plate_id]
    properties_to_copy.append(pygplates.PartitionProperty.valid_time_period)

    pm_manager = PlateModelManager()
    model = pm_manager.get_model(model)

    assigned_point_features = pygplates.partition_into_plates(
        model.get_static_polygons(),
        model.get_rotation_model(),
        point_features,
        properties_to_copy=properties_to_copy,
    )

    reconstructed_feature_geometries = []
    pygplates.reconstruct(
        pygplates.FeatureCollection(assigned_point_features),
        model.get_rotation_model(),
        reconstructed_feature_geometries,
        time,
    )
    lons = len(assigned_point_features) * [None]
    lats = len(assigned_point_features) * [None]
    for rfg in reconstructed_feature_geometries:
        lat, lon = rfg.get_reconstructed_geometry().to_lat_lon()
        name = rfg.get_feature().get_name()
        lons[int(name)] = lon
        lats[int(name)] = lat
    return lons, lats


if __name__ == "__main__":
    unittest.main()
