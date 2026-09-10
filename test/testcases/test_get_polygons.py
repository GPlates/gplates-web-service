import json
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_get_polygons.py


class GetPolygonsTestCase(unittest.TestCase):
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
    def test_coastlines(self):
        """-   testing {}/reconstruct/coastlines?time=100&model=Muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/coastlines",
            params={"time": 100, "model": "Muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertGreater(len(data["features"]), 0)

        msg += r.text[:2000] + "\n"
        self.logger.info(
            "######### test_coastlines ###########\n\n"
            + msg
            + "\n########## end of test_coastlines ##########\n"
        )

    @add_server_url_to_docstring()
    def test_coastlines_png(self):
        """-   testing {}/reconstruct/coastlines?time=100&model=Muller2019&fmt=png"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/coastlines",
            params={"time": 100, "model": "Muller2019", "fmt": "png"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers.get("Content-Type"), "image/png")

        self.logger.info(
            "######### test_coastlines_png ###########\n\n"
            + msg
            + "\n########## end of test_coastlines_png ##########\n"
        )

    @add_server_url_to_docstring()
    def test_coastlines_low(self):
        """-   testing {}/reconstruct/coastlines_low?time=100&model=Muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/coastlines_low",
            params={"time": 100, "model": "Muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertGreater(len(data["features"]), 0)

        msg += r.text[:2000] + "\n"
        self.logger.info(
            "######### test_coastlines_low ###########\n\n"
            + msg
            + "\n########## end of test_coastlines_low ##########\n"
        )

    @add_server_url_to_docstring()
    def test_static_polygons(self):
        """-   testing {}/reconstruct/static_polygons?time=100&model=Muller2019"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/static_polygons",
            params={"time": 100, "model": "Muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertGreater(len(data["features"]), 0)

        msg += r.text[:2000] + "\n"
        self.logger.info(
            "######### test_static_polygons ###########\n\n"
            + msg
            + "\n########## end of test_static_polygons ##########\n"
        )

    @add_server_url_to_docstring()
    def test_static_polygons_with_extent(self):
        """-   testing {}/reconstruct/static_polygons?time=100&model=Muller2019&extent=-180,180,-90,90"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/static_polygons",
            params={
                "time": 100,
                "model": "Muller2019",
                "extent": "-180,180,-90,90",
            },
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertGreater(len(data["features"]), 0)

        msg += r.text[:2000] + "\n"
        self.logger.info(
            "######### test_static_polygons_with_extent ###########\n\n"
            + msg
            + "\n########## end of test_static_polygons_with_extent ##########\n"
        )

    @add_server_url_to_docstring()
    def test_coastlines_time_out_of_scope(self):
        """-   testing {}/reconstruct/coastlines?time=10000&model=Muller2019   (invalid time for the model)"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/coastlines",
            params={"time": 10000, "model": "Muller2019"},
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        msg += r.text + "\n"
        self.assertEqual(r.status_code, 400)

        self.logger.info(
            "######### test_coastlines_time_out_of_scope ###########\n\n"
            + msg
            + "\n########## end of test_coastlines_time_out_of_scope ##########\n"
        )

    @add_server_url_to_docstring()
    def test_flowline(self):
        """-   testing {}/reconstruct/flowline   (endpoint is not yet implemented, should still respond 200)"""
        msg = ""
        r = send_get_request(
            self.SERVER_URL + "/reconstruct/flowline",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"

        msg += r.text + "\n"
        self.assertEqual(r.status_code, 200)

        self.logger.info(
            "######### test_flowline ###########\n\n"
            + msg
            + "\n########## end of test_flowline ##########\n"
        )


if __name__ == "__main__":
    unittest.main()
