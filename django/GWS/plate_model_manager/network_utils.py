import requests

from . import misc_utils


def get_headers(url):
    headers = {"Accept-Encoding": "identity"}
    r = requests.head(url, headers=headers)
    return r.headers


def get_content_length(headers):
    file_size = headers.get("Content-Length")
    try:
        return int(file_size)
    except:
        misc_utils.print_warning("Unable to get the size of the content.")
        return None


def get_etag(headers):
    """return the etag in the headers. The return could be none if the server does not support etag.

    :param headers: call get_headers(url) to get headers

    """
    new_etag = headers.get("ETag")
    if new_etag:
        # remove the content-encoding awareness thing if present
        new_etag = new_etag.replace("-gzip", "")

    return new_etag
