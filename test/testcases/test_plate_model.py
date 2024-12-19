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

# python3 -m unittest -vv test_plate_model.py


class PlateModelTestCase(unittest.TestCase):
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
    def test_list_plate_models(self):
        """-   testing {}/model/list"""
        msg = ""

        r = send_get_request(
            self.SERVER_URL + "/model/list",
        )
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"

        models = json.loads(r.text)

        self.assertGreater(len(models), 0)  # not empty

        self.logger.info(
            "######### test_list_plate_models ###########\n"
            + msg
            + "######### test_list_plate_models ###########\n"
        )

    @add_server_url_to_docstring()
    def test_get_model_info(self):
        """-   testing {}/model/show?model=muller2019"""
        msg = ""

        r = send_get_request(self.SERVER_URL + "/model/show?model=muller2019")
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"
        self.logger.info(
            "######### test_get_model_info ###########\n"
            + msg
            + "\n########## end of test_get_model_info ##########\n"
        )

    @add_server_url_to_docstring()
    def test_get_model_layers(self):
        """-   testing {}/model/list_layers?model=muller2019"""
        msg = ""

        r = send_get_request(self.SERVER_URL + "/model/list_layers?model=muller2019")
        if r.request.url:
            msg += r.request.url + "\n" + str(r.request.headers) + "\n"
        self.assertEqual(r.status_code, 200)

        msg += r.text + "\n"

        layers = json.loads(r.text)
        self.assertGreater(len(layers), 0)  # not empty

        self.logger.info(
            "######### test_get_model_layers ###########\n"
            + msg
            + "\n########## end of test_get_model_layers ##########\n"
        )


if __name__ == "__main__":
    unittest.main()
