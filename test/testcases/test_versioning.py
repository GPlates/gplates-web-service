import logging
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_versioning.py
#
# The versioned alias (/v1/...) must behave exactly like the unversioned URL,
# and every response must say which release answered it. See issue #24.


class VersioningTestCase(unittest.TestCase):
    SERVER_URL = ""
    logger = logging.getLogger()

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem, logging.INFO)
        get_server_url(cls)
        r = send_get_request(cls.SERVER_URL + "/version/")
        cls.version = r.text.strip().strip('"')
        cls.prefix = "/" + cls.version.split(".")[0]  # e.g. "/v1"

    @add_server_url_to_docstring()
    def test_version_header(self):
        """-   testing {}/version/ returns an X-GWS-Version header"""
        r = send_get_request(self.SERVER_URL + "/version/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers.get("X-GWS-Version"), self.version)
        self.assertIn(
            "X-GWS-Version", r.headers.get("Access-Control-Expose-Headers", "")
        )

    @add_server_url_to_docstring()
    def test_versioned_version_endpoint(self):
        """-   testing {}/vN/version/ matches /version/"""
        r = send_get_request(self.SERVER_URL + self.prefix + "/version/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text.strip().strip('"'), self.version)
        self.assertEqual(r.headers.get("X-GWS-Version"), self.version)

    @add_server_url_to_docstring()
    def test_versioned_alias_same_result(self):
        """-   testing {}/vN/reconstruct/reconstruct_points/ matches the unversioned URL"""
        path = "/reconstruct/reconstruct_points/"
        params = {"points": "95,54,142,-33", "time": 140, "model": "MULLER2019"}
        r_plain = send_get_request(self.SERVER_URL + path, params=params)
        r_versioned = send_get_request(
            self.SERVER_URL + self.prefix + path, params=params
        )
        self.assertEqual(r_plain.status_code, 200)
        self.assertEqual(r_versioned.status_code, 200)
        self.assertEqual(r_plain.json(), r_versioned.json())

    @add_server_url_to_docstring()
    def test_header_on_errors(self):
        """-   testing {}/no-such-endpoint/ still carries X-GWS-Version"""
        r = send_get_request(self.SERVER_URL + "/no-such-endpoint/")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.headers.get("X-GWS-Version"), self.version)


if __name__ == "__main__":
    unittest.main()
