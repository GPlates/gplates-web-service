import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from . import network_requests, network_utils

EXPIRY_TIME_FORMAT = "%Y/%m/%d, %H:%M:%S"


def check_redownload_need(metadata_file, url):
    """check the metadata file and decide if redownload is necessary

    :param metadata_file: metadata file path
    :param url: url for the target file

    :returns download_flag, etag: a flag indicates if redownload is neccesarry and old etag if needed.
    """
    download_flag = False
    meta_etag = None
    if os.path.isfile(metadata_file):
        with open(metadata_file, "r") as f:
            meta = json.load(f)
            if "url" in meta:
                meta_url = meta["url"]
                if meta_url != url:
                    # if the data url has changed, re-download
                    download_flag = True
            else:
                download_flag = True

            # if the url is the same, now check the expiry date
            if not download_flag:
                if "expiry" in meta:
                    try:
                        meta_expiry = meta["expiry"]
                        expiry_date = datetime.strptime(meta_expiry, EXPIRY_TIME_FORMAT)
                        now = datetime.now()
                        if now > expiry_date:
                            download_flag = True  # expired
                    except ValueError:
                        download_flag = True  # invalid expiry date
                else:
                    download_flag = True  # no expiry date in metafile

                if download_flag and "etag" in meta:
                    meta_etag = meta["etag"]
    else:
        download_flag = True  # if metadata_file does not exist

    return download_flag, meta_etag


def download_file(url, metadata_file, dst_path, expire_hours=12, large_file_hint=False):
    """download a file from "url", save the file in "dst_path" and write the metadata
    a metadata file will also be created for the file

    :param url: the url to the raster file
    :param metadata_file: the path to the metadata
    :param dst_path: the folder path to save the raster file

    """
    print(f"downloading {url}")
    download_flag, etag = check_redownload_need(metadata_file, url)

    file_size = None
    if download_flag and large_file_hint:
        # check the file size and etag for large file
        headers = network_utils.get_headers(url)
        file_size = network_utils.get_content_length(headers)
        new_etag = network_utils.get_etag(headers)
        if etag is not None and etag == new_etag:
            download_flag = False

    # only redownload when necessary
    if download_flag:
        if file_size and file_size > 20 * 1000 * 1000:
            new_etag = network_requests.fetch_large_file(
                url, dst_path, filesize=file_size, auto_unzip=True, check_etag=False
            )
        else:
            new_etag = network_requests.fetch_file(
                url,
                dst_path,
                etag=etag,
                auto_unzip=True,
            )
        if etag != new_etag or new_etag is None:
            # save metadata file
            metadata = {
                "url": url,
                "expiry": (datetime.now() + timedelta(hours=expire_hours)).strftime(
                    EXPIRY_TIME_FORMAT
                ),
                "etag": new_etag,
            }
            Path("/".join(metadata_file.split("/")[:-1])).mkdir(
                parents=True, exist_ok=True
            )
            with open(metadata_file, "w+") as f:
                json.dump(metadata, f)
    else:
        print("The local files are still good. Will not download again.")
