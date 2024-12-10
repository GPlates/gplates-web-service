import copy
import json
import math
import unittest, logging
from pathlib import Path
from collections.abc import Sequence

import requests
from common import (
    get_server_url,
    get_test_flag,
    setup_logger,
    add_server_url_to_docstring,
    send_get_request,
    send_post_request,
)
from plate_model_manager import PlateModelManager

# python3 -m unittest -vv test_reconstruct_points.py


class ReconstructPointsTestCase(unittest.TestCase):
    SERVER_URL = ""
    logger = logging.getLogger()

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)
        cls.proxies = {"http": ""}
        cls.data_1 = {
            "points": "95, 54, 142, -33",
            "time": 140,
            "model": "Muller2019",
        }
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

    @add_server_url_to_docstring()
    def test_basic_get(self):
        """testing {}/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=Muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=self.data_1,
        )
        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))

        self.assertEqual(r.status_code, 200)

        try:
            gws_return_data = json.loads(str(r.text))
            msg += json.dumps(gws_return_data, sort_keys=True, indent=4) + "\n"
        except Exception as e:
            self.logger.info("invalid return data: " + r.text)
            self.assertTrue(False)
            raise e

        if get_test_flag("GWS_TEST_VALIDATE_WITH_PYGPLATES"):
            msg += "validate results with pygplates.....\n"
            ps = self.data_1["points"].split(",")
            lats = ps[1::2]
            lons = ps[0::2]
            rlons, rlats = _reconstruct(
                lons, lats, self.data_1["model"], self.data_1["time"]
            )
            for i in range(len(rlons)):
                msg += f"{gws_return_data['coordinates'][int(i)][0]}, {rlons[i]}\n"
                msg += f"{gws_return_data['coordinates'][int(i)][1]}, {rlats[i]}\n"

                rr = rlons[i]
                if rr is not None:
                    true_or_false = math.isclose(
                        gws_return_data["coordinates"][int(i)][0],
                        rr,
                        abs_tol=0.0001,
                    )
                    self.assertTrue(true_or_false)

                rr = rlats[i]
                if rr is not None:
                    self.assertTrue(
                        math.isclose(
                            gws_return_data["coordinates"][int(i)][1],
                            rr,
                            abs_tol=0.0001,
                        )
                    )

        self.logger.info(
            "######### test_basic_get ###########\n"
            + msg
            + "\n######### test_basic_get ###########\n"
        )

    @add_server_url_to_docstring()
    def test_basic_post(self):
        """testing {}/reconstruct/reconstruct_points/  (HTTP POST method)"""
        msg = ""
        r = send_post_request(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=self.data_1,
        )
        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))

        self.assertEqual(r.status_code, 200)

        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"

        self.logger.info(
            "######### test_basic_post ###########\n"
            + msg
            + "\n######### test_basic_post ###########\n"
        )

    @add_server_url_to_docstring()
    def test_post_return_feature_collection(self):
        """testing {}/reconstruct/reconstruct_points/?fc=true (HTTP POST method)"""
        msg = ""
        data = copy.copy(self.data_2)
        data["fc"] = True
        r = send_post_request(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=data,
        )

        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))
        self.assertEqual(r.status_code, 200)

        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"
        self.logger.info(
            "######### test_post_return_feature_collection ###########\n"
            + msg
            + "\n######### test_post_return_feature_collection ###########\n"
        )

    @add_server_url_to_docstring()
    def test_get_return_feature_collection(self):
        """testing {}/reconstruct/reconstruct_points/?fc=true (HTTP GET method)"""
        msg = ""
        data = copy.copy(self.data_2)
        data["fc"] = True
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
        )
        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))

        self.assertEqual(r.status_code, 200)

        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"
        self.logger.info(
            "######### test_get_return_feature_collection ###########\n"
            + msg
            + "\n######### test_get_return_feature_collection ###########\n"
        )

    @add_server_url_to_docstring()
    def test_get_multi_times(self):
        """testing {}/reconstruct/reconstruct_points/   (HTTP GET method with multiple times)"""
        msg = ""
        data = copy.copy(self.data_3)
        data["fc"] = "False"
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
        )
        try:
            gws_return_data = json.loads(str(r.text))
            msg += json.dumps(gws_return_data, sort_keys=True, indent=4) + "\n"
        except Exception as e:
            msg += r.text + "\n"
            self.assertTrue(False)
            raise e

        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))
        self.assertEqual(r.status_code, 200)

        if get_test_flag("GWS_TEST_VALIDATE_WITH_PYGPLATES"):
            msg += "validate results with pygplates.....\n"
            for time in self.data_3["times"].split(","):
                rlons, rlats = _reconstruct(
                    self.data_3["lons"].split(","),
                    self.data_3["lats"].split(","),
                    self.data_3["model"],
                    float(time),
                )
                for i in range(len(rlons)):
                    rlon = rlons[i]
                    if rlon is None:
                        rlon = 999.99
                    rlat = rlats[i]
                    if rlat is None:
                        rlat = 999.99

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
        self.logger.info(
            "######### test_get_multi_times ###########\n"
            + msg
            + "\n######### test_get_multi_times ###########\n"
        )

    @add_server_url_to_docstring()
    def test_post_multi_times(self):
        """testing {}/reconstruct/reconstruct_points/   (HTTP POST method with multiple times)"""
        msg = ""
        data = copy.copy(self.data_3)
        data["fc"] = "True"
        r = send_post_request(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=data,
        )

        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))
        self.assertEqual(r.status_code, 200)

        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"
        self.logger.info(
            "######### test_post_multi_times ###########\n"
            + msg
            + "\n######### test_post_multi_times ###########\n"
        )

    @add_server_url_to_docstring()
    def test_get_with_pid(self):
        """testing {}/reconstruct/reconstruct_points/  (with a single plate ID)"""
        msg = ""
        data = copy.copy(self.data_1)
        data["pid"] = 701
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
        )

        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))
        self.assertEqual(r.status_code, 200)

        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"
        self.logger.info(
            "######### test_get_with_pid ###########\n"
            + msg
            + "\n######### test_get_with_pid ###########\n"
        )

    @add_server_url_to_docstring()
    def test_get_with_pids(self):
        """testing {}/reconstruct/reconstruct_points/  (with a list of plate IDs)"""
        msg = ""
        data = copy.copy(self.data_1)
        data["pids"] = "701, 801"
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=self.data_1,
        )

        if r.request.url:
            self.logger.debug(r.request.url + str(r.request.headers))

        self.assertEqual(r.status_code, 200)

        msg += json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4) + "\n"
        self.logger.info(
            "######### test_get_with_pids ###########\n"
            + msg
            + "\n######### test_get_with_pids ###########\n"
        )

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

    def test_get_ignore_valid_time_ex(self):
        data = copy.copy(self.data_4)
        data["ignore_valid_time"] = "True"

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
        data["return_null_points"] = "True"

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

    def test_time_out_of_scope(self):
        data = copy.copy(self.data_3)
        data["times"] += ",10000"

        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(" test_time_out_of_scope: " + r.text)
        self.assertEqual(r.status_code, 400)

        data = copy.copy(self.data_1)
        data["time"] = 10000

        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(" test_time_out_of_scope: " + r.text)
        self.assertEqual(r.status_code, 400)

    def test_various_coordinates_input(self):
        data = {
            "lat": 50,
            "lon": -100,
            "time": 100,
            "model": "PALEOMAP",
        }
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info("test_various_coordinates_input: " + r.text)
        self.assertEqual(r.status_code, 200)

        data = {
            "point": "-100,50",
            "time": 100,
            "model": "PALEOMAP",
        }
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info("test_various_coordinates_input: " + r.text)
        self.assertEqual(r.status_code, 200)

        data = {
            "point": "[-100,50]",
            "time": 100,
            "model": "PALEOMAP",
        }
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info("test_various_coordinates_input: " + r.text)
        self.assertEqual(r.status_code, 200)

        data = {
            "points": "[[-100,50],[95, 54], [142, -33]]",
            "time": 100,
            "model": "PALEOMAP",
        }
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info("test_various_coordinates_input: " + r.text)
        self.assertEqual(r.status_code, 200)

        data = {
            "points": "[100, 33, 50, 44, 0, 55]",
            "time": 100,
            "model": "PALEOMAP",
        }
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info("test_various_coordinates_input: " + r.text)
        self.assertEqual(r.status_code, 200)

        data = {
            "point": "[50,-100]",
            "time": 100,
            "model": "PALEOMAP",
        }
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info("test_various_coordinates_input: " + r.text)
        self.assertEqual(r.status_code, 400)


def _reconstruct(
    lons: list, lats: list, model: str, time: int | float
) -> tuple[Sequence[float | None], Sequence[float | None]]:
    import pygplates

    point_features = []
    p_index = 0
    for lat, lon in zip(lats, lons):
        point_feature = pygplates.Feature()  # type: ignore
        point_feature.set_geometry(pygplates.PointOnSphere(float(lat), float(lon)))  # type: ignore
        point_feature.set_name(str(p_index))
        point_features.append(point_feature)
        p_index += 1

    properties_to_copy = [pygplates.PartitionProperty.reconstruction_plate_id]  # type: ignore
    properties_to_copy.append(pygplates.PartitionProperty.valid_time_period)  # type: ignore

    pm_manager = PlateModelManager()
    mm = pm_manager.get_model(model)
    if not mm:
        raise Exception(f"Unable to get model {model}")

    assigned_point_features = pygplates.partition_into_plates(  # type: ignore
        mm.get_static_polygons(),
        mm.get_rotation_model(),
        point_features,
        properties_to_copy=properties_to_copy,
    )

    reconstructed_feature_geometries = []
    pygplates.reconstruct(  # type: ignore
        pygplates.FeatureCollection(assigned_point_features),  # type: ignore
        mm.get_rotation_model(),
        reconstructed_feature_geometries,
        time,
    )
    rlons = len(assigned_point_features) * [None]
    rlats = len(assigned_point_features) * [None]
    for rfg in reconstructed_feature_geometries:
        lat, lon = rfg.get_reconstructed_geometry().to_lat_lon()
        name = rfg.get_feature().get_name()
        rlons[int(name)] = lon
        rlats[int(name)] = lat
    return rlons, rlats


if __name__ == "__main__":
    unittest.main()
