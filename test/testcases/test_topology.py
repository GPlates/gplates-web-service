import json
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_topology.py


class TopologyTestCase(unittest.TestCase):
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
    def test_plate_boundaries(self):
        """-   testing {}/topology/plate_boundaries?time=100&model=Muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/topology/plate_boundaries",
            params={"time": 100, "model": "Muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertGreater(len(data["features"]), 0)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_plate_boundaries ###########\n\n"
            + msg
            + "\n########## end of test_plate_boundaries ##########\n"
        )

    @add_server_url_to_docstring()
    def test_plate_polygons(self):
        """-   testing {}/topology/plate_polygons?time=100&model=Muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/topology/plate_polygons",
            params={"time": 100, "model": "Muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertGreater(len(data["features"]), 0)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_plate_polygons ###########\n\n"
            + msg
            + "\n########## end of test_plate_polygons ##########\n"
        )

    @add_server_url_to_docstring()
    def test_plate_polygons_as_lines(self):
        """-   testing {}/topology/plate_polygons?time=100&model=Muller2019&as_lines=true"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/topology/plate_polygons",
            params={"time": 100, "model": "Muller2019", "as_lines": "true"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertEqual(data["type"], "FeatureCollection")

        msg += r.text + "\n"
        self.logger.info(
            "######### test_plate_polygons_as_lines ###########\n\n"
            + msg
            + "\n########## end of test_plate_polygons_as_lines ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_subduction_zones(self):
        """-   testing {}/topology/get_subduction_zones?time=100&model=Muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/topology/get_subduction_zones",
            params={"time": 100, "model": "Muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertEqual(data["type"], "FeatureCollection")

        msg += r.text + "\n"
        self.logger.info(
            "######### test_get_subduction_zones ###########\n\n"
            + msg
            + "\n########## end of test_get_subduction_zones ##########\n"
        )


if __name__ == "__main__":
    unittest.main()
