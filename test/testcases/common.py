import logging
import os
from pathlib import Path

import urllib3


def setup_logger(cls, name):
    cls.logger = logging.getLogger(name)
    cls.logger.setLevel(logging.INFO)
    cls.logger.propagate = False
    Path("logs").mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(f"logs/{name}.log")
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s {%(pathname)s:%(lineno)d} \n\n%(message)s\n "
    )
    fh.setFormatter(formatter)
    cls.logger.addHandler(fh)

    # print(self.logger.handlers)
    urllib3.disable_warnings()


def get_server_url(cls):
    cls.SERVER_URL = os.getenv("GWS_SERVER_URL")

    if not cls.SERVER_URL:
        cls.SERVER_URL = "http://127.0.0.1:18000"
        # print(cls.logger)
        cls.logger.info(f"Using server URL in script {cls.SERVER_URL}")
    else:
        cls.logger.info(f"Using server URL in environment variable {cls.SERVER_URL}")


def get_test_level():
    try:
        return int(os.getenv("GWS_TEST_LEVEL", 0))
    except:
        return 0  # default test level 0


def get_test_flag(env_var, default_var="false"):
    flag = os.getenv(env_var, default_var)
    if flag.lower().strip() in ["true", "1"]:
        return True
    else:
        return False
