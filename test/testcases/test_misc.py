import json
import logging
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_misc.py

# pay attention here !!! this testcase can reveal some excessive memory usage issue.


class MiscTestCase(unittest.TestCase):
    SERVER_URL = ""
    logger = logging.getLogger()

    def setUp(self):
        pass

    def tearDown(self):
        self.logger.debug("tearDown")

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem, logging.INFO)
        get_server_url(cls)

    @classmethod
    def tearDownClass(cls):
        cls.logger.debug("tearDownClass")

    @add_server_url_to_docstring()
    def test_motion_path(self):
        """-   testing {}/reconstruct/motion_path?seedpoints=0,0&movplate=701"""
        msg = ""
        data = {"seedpoints": "0,0", "movplate": 701}
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/motion_path",
            params=data,
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_motion_path ###########\n"
            + msg
            + "######### test_motion_path ###########\n"
        )

    @add_server_url_to_docstring()
    def test_interp_two_locations(self):
        """-   testing {}/earth/interp_two_locations?point_a=120,45&point_b=20,-45&num=10"""
        msg = ""
        data = {"point_a": "120,45", "point_b": "20,-45", "num": 10}
        r = send_get_request(
            self.SERVER_URL + "/earth/interp_two_locations", params=data
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_interp_two_locations ###########\n"
            + msg
            + "\n########## end of test_interp_two_locations ##########\n"
        )

    @add_server_url_to_docstring()
    def test_distance(self):
        """-   testing {}/earth/distance?point_a=120,45&point_b=20,-45"""
        msg = ""
        data = {"point_a": "120,45", "point_b": "20,-45"}
        r = send_get_request(self.SERVER_URL + "/earth/distance", params=data)
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"

        dist = json.loads(r.text)
        self.assertAlmostEqual(dist["distance"], 14018, delta=1)
        self.logger.info(
            "######### test_distance ###########\n"
            + msg
            + "\n########## end of test_distance ##########\n"
        )

    @add_server_url_to_docstring()
    def test_paleo_cities(self):
        """-   testing {}/earth/get_cities?time=100&model=muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/earth/get_cities",
            params={"time": 100, "model": "muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"

        return_data = json.loads(str(r.text))
        self.logger.info(
            "######### test_paleo_cities ###########\n"
            + msg
            + "\n########## end of test_paleo_cities ##########\n"
        )

        self.assertEqual(len(return_data["names"]), len(return_data["lons"]))
        self.assertEqual(len(return_data["names"]), len(return_data["lats"]))

    @add_server_url_to_docstring()
    def test_get_present_day_cities(self):
        """-   testing {}/earth/get_present_day_cities"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/earth/get_present_day_cities",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        self.assertEqual(r.status_code, 200)
        msg += r.text + "\n"
        self.logger.info(
            "######### test_get_present_day_cities ###########\n"
            + msg
            + "\n########## end of test_get_present_day_cities ##########\n"
        )

    @add_server_url_to_docstring()
    def test_paleo_labels(self):
        """-   testing {}/earth/get_labels?time=300&model=merdith2021"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/earth/get_labels",
            params={"time": 300, "model": "merdith2021"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        self.assertEqual(r.status_code, 200)
        msg += r.text + "\n"
        self.logger.info(
            "######### test_paleo_labels ###########\n"
            + msg
            + "\n########## end of test_paleo_labels ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_plate_names(self):
        """-   testing {}/earth/get_plate_names"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/earth/get_plate_names",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        self.assertEqual(r.status_code, 200)
        msg += r.text[:2000] + "\n"

        plate_names = json.loads(r.text)
        self.assertGreater(len(plate_names), 0)

        self.logger.info(
            "######### test_get_plate_names ###########\n"
            + msg
            + "\n########## end of test_get_plate_names ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_globe_mesh(self):
        """-   testing {}/earth/get_globe_mesh?level=2"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/earth/get_globe_mesh",
            params={"level": 2},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        self.assertEqual(r.status_code, 200)
        msg += r.text[:2000] + "\n"

        mesh = json.loads(r.text)
        self.assertGreater(len(mesh["vertices"]), 0)
        self.assertGreater(len(mesh["faces"]), 0)

        self.logger.info(
            "######### test_get_globe_mesh ###########\n"
            + msg
            + "\n########## end of test_get_globe_mesh ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_globe_mesh_invalid_level(self):
        """-   testing {}/earth/get_globe_mesh?level=8   (level exceeds the maximum allowed value of 7)"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/earth/get_globe_mesh",
            params={"level": 8},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        msg += r.text + "\n"
        self.assertEqual(r.status_code, 400)

        self.logger.info(
            "######### test_get_globe_mesh_invalid_level ###########\n"
            + msg
            + "\n########## end of test_get_globe_mesh_invalid_level ##########\n"
        )

    @add_server_url_to_docstring()
    def test_paleolithology(self):
        """-   testing {}/earth/paleolithology?time=100&model=muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/earth/paleolithology",
            params={"time": 100, "model": "muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        self.assertEqual(r.status_code, 200)
        msg += r.text[:2000] + "\n"
        self.logger.info(
            "######### test_paleolithology ###########\n"
            + msg
            + "\n########## end of test_paleolithology ##########\n"
        )

    @add_server_url_to_docstring()
    def test_paleomagnetism(self):
        """-   testing {}/earth/paleomagnetism?time=100&model=muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/earth/paleomagnetism",
            params={"time": 100, "model": "muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        self.assertEqual(r.status_code, 200)
        msg += r.text[:2000] + "\n"
        self.logger.info(
            "######### test_paleomagnetism ###########\n"
            + msg
            + "\n########## end of test_paleomagnetism ##########\n"
        )

    @add_server_url_to_docstring()
    def test_version(self):
        """-   testing {}/version"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/version",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        self.assertEqual(r.status_code, 200)
        msg += r.text + "\n"
        self.logger.info(
            "######### test_version ###########\n"
            + msg
            + "\n########## end of test_version ##########\n"
        )


if __name__ == "__main__":
    unittest.main()
