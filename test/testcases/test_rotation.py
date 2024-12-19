import json
import random
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    get_test_flag,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_rotation.py

# if GWS_TEST_VALIDATE_WITH_PYGPLATES is enabled, you need to install pygplates, plate_model_manager and gwspy


class RotationTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        self.logger.debug("tearDown")

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)

    @classmethod
    def tearDownClass(cls):
        cls.logger.debug("tearDownClass")

    @add_server_url_to_docstring()
    def test_rotate(self):
        """-   testing {}/rotation/rotate/?point=120,45&axis=20,-45&angle=20"""
        msg = ""
        data = {"point": "120,45", "axis": "20,-45", "angle": 20}
        r = send_get_request(
            self.SERVER_URL + "/rotation/rotate",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_rotate ###########\n\n"
            + msg
            + "\n########## end of test_rotate ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_plate_ids(self):
        """-   testing {}/rotation/get_plate_ids?time=100"""
        msg = ""

        r = send_get_request(
            self.SERVER_URL + "/rotation/get_plate_ids?time=100",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        pids = json.loads(str(r.text))
        self.assertTrue(len(pids) > 0)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_get_plate_ids ###########\n\n"
            + msg
            + "\n########## end of test_get_plate_ids ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_euler_pole_and_angle(self):
        """-   testing {}/rotation/get_euler_pole_and_angle?time=100&pids=801"""
        msg = ""
        model_name = "MULLER2019"
        time = 100
        pid = 801
        r = send_get_request(
            self.SERVER_URL + "/rotation/get_euler_pole_and_angle",
            params={"times": time, "pids": pid, "model": model_name},
        )

        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"

        if get_test_flag("GWS_TEST_VALIDATE_WITH_PYGPLATES"):
            import math

            import pygplates
            from gwspy import rotation
            from plate_model_manager import PlateModelManager

            # define a random test point
            test_point = [
                random.randint(-90, 90),
                random.randint(-180, 180),
            ]  # lat, lon
            model = PlateModelManager().get_model(model_name)
            rotation_model = pygplates.RotationModel(model.get_rotation_model())

            # rotate the test point with pygplates
            rotated_points = rotation_model.get_rotation(
                float(time), pid
            ) * pygplates.PointOnSphere(test_point)
            pygplates_lat, pygplates_lon = rotated_points.to_lat_lon()
            msg += f"pygplates: {pygplates_lat}, {pygplates_lon}\n"

            pole_and_angle = json.loads(r.text)
            pole_and_angle = pole_and_angle[str(float(time))][str(pid)]
            lat, lon = rotation.rotate(
                [math.radians(test_point[0]), math.radians(test_point[1])],
                [math.radians(pole_and_angle[1]), math.radians(pole_and_angle[0])],
                math.radians(pole_and_angle[2]),
            )
            euler_lat = math.degrees(lat)
            euler_lon = math.degrees(lon)
            msg += f"euler pole and angle: {euler_lat}, {euler_lon} \n"

            self.assertAlmostEqual(pygplates_lat, euler_lat, delta=0.0001)
            self.assertAlmostEqual(pygplates_lon, euler_lon, delta=0.0001)

        self.logger.info(
            "######### test_get_euler_pole_and_angle ###########\n\n"
            + msg
            + "\n########## end of test_get_euler_pole_and_angle ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_quaternions(self):
        """-   testing {}/rotation/get_quaternions?time=100&pids=801"""
        msg = ""
        model_name = "MULLER2019"
        time = 100
        pid = 801
        r = send_get_request(
            f"{self.SERVER_URL}/rotation/get_quaternions/",
            params={"times": time, "pids": pid, "model": model_name},
        )

        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"

        if get_test_flag("GWS_TEST_VALIDATE_WITH_PYGPLATES"):
            import math

            import pygplates
            from gwspy import quaternions
            from plate_model_manager import PlateModelManager

            # define a random test point
            test_point = [
                random.randint(-90, 90),
                random.randint(-180, 180),
            ]  # lat, lon
            model = PlateModelManager().get_model(model_name)
            rotation_model = pygplates.RotationModel(model.get_rotation_model())

            # rotate the test point with pygplates
            rotated_points = rotation_model.get_rotation(
                float(time), pid
            ) * pygplates.PointOnSphere(test_point)
            pygplates_lat, pygplates_lon = rotated_points.to_lat_lon()
            msg += f"pygplates: {pygplates_lat}, {pygplates_lon}\n"

            quat = json.loads(r.text)
            quat = quat[str(float(time))][str(pid)]
            v = quaternions.lat_lon_to_cart(
                math.radians(test_point[0]), math.radians(test_point[1])
            )
            ret = quaternions.quat_vec_mult(quat, v)
            quat_lat, quat_lon = quaternions.cart_to_lat_lon(ret[0], ret[1], ret[2])
            quat_lon = math.degrees(quat_lon)
            quat_lat = math.degrees(quat_lat)
            msg += f"quaternions: {quat_lat}, {quat_lon} \n"

            self.assertAlmostEqual(pygplates_lat, quat_lat, delta=0.0001)
            self.assertAlmostEqual(pygplates_lon, quat_lon, delta=0.0001)

        self.logger.info(
            "######### test_get_quaternions ###########\n\n"
            + msg
            + "\n########## end of test_get_quaternions ##########\n"
        )

    @add_server_url_to_docstring()
    def test_rotation_map(self):
        """-   testing {}/rotation/get_rotation_map?model=MERDITH2021"""
        msg = ""

        r = send_get_request(
            self.SERVER_URL + "/rotation/get_rotation_map/?model=MERDITH2021",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_rotation_map ###########\n\n"
            + msg
            + "\n########## end of test_rotation_map ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_reconstruction_tree_edges(self):
        """-   testing {}/rotation/get_reconstruction_tree_edges?model=seton2012&level=4&pids=707,702,314,833"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL
            + "/rotation/get_reconstruction_tree_edges/?model=seton2012&level=4&pids=707,702,314,833",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_get_reconstruction_tree_edges ###########\n\n"
            + msg
            + "\n########## end of test_get_reconstruction_tree_edges ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_reconstruction_tree_height(self):
        """-   testing {}/rotation/get_reconstruction_tree_height"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/rotation/get_reconstruction_tree_height",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_get_reconstruction_tree_height ###########\n\n"
            + msg
            + "\n########## end of test_get_reconstruction_tree_height ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_reconstruction_tree_leaves(self):
        """-   testing {}/rotation/get_reconstruction_tree_leaves"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/rotation/get_reconstruction_tree_leaves",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_get_reconstruction_tree_leaves ###########\n\n"
            + msg
            + "\n########## end of test_get_reconstruction_tree_leaves ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_ancestors_in_reconstruction_tree(self):
        """-   testing {}/rotation/get_ancestors_in_reconstruction_tree/?pid=801"""
        msg = ""

        r = send_get_request(
            self.SERVER_URL
            + f"/rotation/get_ancestors_in_reconstruction_tree/?pid=801",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_get_ancestors_in_reconstruction_tree ###########\n\n"
            + msg
            + "\n########## end of test_get_ancestors_in_reconstruction_tree ##########\n"
        )

    @add_server_url_to_docstring()
    def test_find_axis_and_angle(self):
        """-   testing {}/earth/find_axis_and_angle?point_a=120,45&point_b=20,-45"""
        msg = ""
        data = {"point_a": "120,45", "point_b": "20,-45"}
        r = send_get_request(
            self.SERVER_URL + "/earth/find_axis_and_angle",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_find_axis_and_angle ###########\n"
            + msg
            + "######### test_find_axis_and_angle ###########\n"
        )


if __name__ == "__main__":
    unittest.main()
