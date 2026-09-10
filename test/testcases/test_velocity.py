import json
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_velocity.py
#
# use domain_type=healpix to keep the domain point count (and the request
# time) reasonable -- the default longLatGrid domain is a global 1-degree
# mesh and is very slow to compute.


class VelocityTestCase(unittest.TestCase):
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
    def test_velocity_static_polygons(self):
        """-   testing {}/velocity/static_polygons?time=100&domain_type=healpix"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/velocity/static_polygons",
            params={"time": 100, "domain_type": "healpix"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertGreater(len(data["coordinates"]), 0)

        msg += r.text[:2000] + "\n"
        self.logger.info(
            "######### test_velocity_static_polygons ###########\n\n"
            + msg
            + "\n########## end of test_velocity_static_polygons ##########\n"
        )

    @add_server_url_to_docstring()
    def test_velocity_static_polygons_east_north(self):
        """-   testing {}/velocity/static_polygons?time=100&domain_type=healpix&velocity_type=east_north"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/velocity/static_polygons",
            params={
                "time": 100,
                "domain_type": "healpix",
                "velocity_type": "east_north",
            },
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertGreater(len(data["coordinates"]), 0)

        msg += r.text[:2000] + "\n"
        self.logger.info(
            "######### test_velocity_static_polygons_east_north ###########\n\n"
            + msg
            + "\n########## end of test_velocity_static_polygons_east_north ##########\n"
        )

    @add_server_url_to_docstring()
    def test_velocity_plate_polygons(self):
        """-   testing {}/velocity/plate_polygons?time=100&domain_type=healpix"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/velocity/plate_polygons",
            params={"time": 100, "domain_type": "healpix"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertGreater(len(data["coordinates"]), 0)

        msg += r.text[:2000] + "\n"
        self.logger.info(
            "######### test_velocity_plate_polygons ###########\n\n"
            + msg
            + "\n########## end of test_velocity_plate_polygons ##########\n"
        )


if __name__ == "__main__":
    unittest.main()
