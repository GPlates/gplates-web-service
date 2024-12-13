import json
import random
import unittest
from pathlib import Path

import requests
from common import (
    add_server_url_to_docstring,
    get_server_url,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_rotation.py


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

        r = send_get_request(
            self.SERVER_URL + "/rotation/get_euler_pole_and_angle",
            params={"times": 100, "pids": 801},
        )

        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_get_euler_pole_and_angle ###########\n\n"
            + msg
            + "\n########## end of test_get_euler_pole_and_angle ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_quaternions(self):
        """-   testing {}/rotation/get_quaternions?time=100&pids=801"""
        msg = ""

        r = send_get_request(
            f"{self.SERVER_URL}/rotation/get_quaternions/",
            params={"times": 100, "pids": 801},
        )

        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
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


if __name__ == "__main__":
    unittest.main()
