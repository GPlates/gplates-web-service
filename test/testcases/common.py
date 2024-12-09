import logging
import os
import time
from enum import Enum
from functools import wraps
from pathlib import Path

import requests
import urllib3


def setup_logger(cls, name: str, level=logging.INFO):
    cls.logger = logging.getLogger(name)
    cls.logger.setLevel(level)
    cls.logger.propagate = False
    Path("logs").mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(f"logs/{name}.log")
    fh.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s {%(pathname)s:%(lineno)d} \n\n%(message)s\n "
    )
    fh.setFormatter(formatter)
    cls.logger.addHandler(fh)

    # print(self.logger.handlers)
    urllib3.disable_warnings()


def get_server_url(cls=None) -> str:
    msg = "Using server URL in environment variable GWS_SERVER_URL: {}"
    url = os.getenv("GWS_SERVER_URL")
    if not url:
        url = "http://127.0.0.1:18000"
        msg = "Using default server URL {}"

    if cls is not None:
        cls.SERVER_URL = url
        cls.logger.info(msg.format(cls.SERVER_URL))
    return url


def get_test_level():
    """return an integer number to indicate the test level
    the higher test level, the more testcases"""
    try:
        return int(os.getenv("GWS_TEST_LEVEL", 0))
    except:
        return 0  # default test level 0


def get_test_flag(env_var, default_var="false"):
    """get the value of a test flag, such as GWS_TEST_DB_QUERY, GWS_TEST_VALIDATE_WITH_PYGPLATES
    return True or False"""
    flag = os.getenv(env_var, default_var)
    if flag.lower().strip() in ["true", "1"]:
        return True
    else:
        return False


class HttpMethod(Enum):
    GET = 1
    POST = 2


def _send_request(
    url: str, data: dict = {}, delay: float = 0.0, method: HttpMethod = HttpMethod.GET
) -> requests.Response:
    """a wrapper to send http(s) GET/POST request via 'requests'
    we can insert time delay for each request by using this wrapper"""
    if delay > 0.0:
        time.sleep(delay)
    else:
        try:
            d = float(os.getenv("GWS_TEST_DELAY", 0.0))
            if d > 0.0:
                time.sleep(d)
        except:
            pass

    if method == HttpMethod.GET:
        return requests.get(
            url,
            params=data,
            verify=False,
            proxies={
                "http": ""
            },  # TODO: set the proxy via environment variable, for example GWS_TEST_PROXY.
        )
    elif method == HttpMethod.POST:
        return requests.post(
            url,
            data=data,
            verify=False,
            proxies={
                "http": ""
            },  # TODO: set the proxy via environment variable, for example GWS_TEST_PROXY.
        )
    else:
        raise Exception(f"Unknown Http method: {method}")


def send_get_request(
    url: str, params: dict = {}, delay: float = 0.0
) -> requests.Response:
    return _send_request(url, params, delay, method=HttpMethod.GET)


def send_post_request(
    url: str, data: dict = {}, delay: float = 0.0
) -> requests.Response:
    return _send_request(url, data, delay, method=HttpMethod.POST)


def add_server_url_to_docstring():
    """add the server's URL to the function's __doc__"""

    def inner(func_pointer):
        if func_pointer.__doc__:
            func_pointer.__doc__ = func_pointer.__doc__.format(get_server_url())

        @wraps(func_pointer)
        def wrapper(*args, **kwargs):
            return func_pointer(*args, **kwargs)

        return wrapper

    return inner
