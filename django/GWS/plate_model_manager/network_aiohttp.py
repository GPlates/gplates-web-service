import asyncio
import io
import os
from pathlib import Path

import aiohttp

from . import unzip_utils
from .file_fetcher import FileFetcher

# This file contains experimental code to download files concurrently using aiohttp.
# Later, I realized that "requests"+"ThreadPoolExecutor" works as well.
# I do not want to introduce a new dependency when "requests" works.
# So, keep this file just for record keeping in case we need aiohttp in the future.


class AiohttpFetcher(FileFetcher):
    def __init__(self):
        pass

    def fetch_file(
        self,
        url: str,
        filepath: str,
        etag: str = None,
        auto_unzip: bool = True,
    ):
        """download a file from "url" and save to "filepath"
            You can give a new "filename" for the file.
            If "etag" is given, check if etag has changed. If not changed, do not download again.

        :param url: the url to download file from
        :param filepath: location to keep the file
        :param etag: old etag. if the old etag is the same with the one on server, do not download again.
        :param auto_unzip: bool flag to indicate if unzip .zip file automatically

        """

        async def f():
            async with aiohttp.ClientSession() as session:
                await self._fetch_file(
                    session,
                    url,
                    filepath,
                    etag=etag,
                    auto_unzip=auto_unzip,
                )

        asyncio.run(f())

    async def _fetch_file(
        self,
        session,
        url: str,
        filepath: str,
        etag: str = None,
        auto_unzip: bool = True,
    ):
        """async "fetch_file" implementation. See the docstring of "fetch_file" """

        if etag:
            headers = {"If-None-Match": etag}
        else:
            headers = {}

        if os.path.isfile(filepath):
            raise Exception(
                f"The 'filepath' is in fact a file. The 'filepath' should be a folder path(non-exist is fine). {filepath}"
            )
        Path(filepath).mkdir(parents=True, exist_ok=True)

        async with session.get(url, headers=headers) as r:
            content = await r.content.read()
            # r = requests.get(url, allow_redirects=True, headers=headers)
            # print(r.headers)

            if r.status == 304:
                print(url)
                print(
                    "The file has not been changed since it was downloaded last time. Do nothing and return."
                )
            elif r.status == 200:
                filename = url.split("/")[-1]  # use the filename in the url
                if auto_unzip:
                    try:
                        unzip_utils.save_compressed_data(
                            url, io.BytesIO(content), filepath
                        )
                    except Exception as ex:
                        # print(ex)
                        self._save_file(filepath, filename, content)
                else:
                    self._save_file(filepath, filename, content)
            else:
                raise Exception(f"HTTP request failed with code {r.status_code}.")
            new_etag = r.headers.get("ETag")
            if new_etag:
                # remove the content-encoding awareness thing
                new_etag = new_etag.replace("-gzip", "")

            return new_etag

    async def _fetch_range(
        self, session, url: str, index: int, chunk_size: int, data: list
    ):
        """async funtion to get patial content of a file from the server
        Be careful, some server does not support this function.
        And some firewall sequences these requests to shape network traffic and defeat the purpose
        of this function completely.

        """
        # print(index)
        # st = time.time()
        headers = {
            "Range": f"bytes={index*chunk_size}-{(index+1)*chunk_size-1}",
            "Accept-Encoding": "identity",
        }

        # r = requests.get(url, headers=headers)
        async with session.get(url, headers=headers) as r:
            if r.status == 206:
                c = await r.content.read()
                data[index].write(c)
            else:
                raise Exception(f"Failed to fetch range from {url} at index {index}")
        # et = time.time()
        # print(f"{index} -- time: {et - st}")

    async def _fetch_large_file(
        self, url: str, file_size: int, data: list, chunk_size=10 * 1000 * 1000
    ):
        """async implementation of fetch_large_file"""
        async with aiohttp.ClientSession() as session:
            num_chunks = file_size // chunk_size + 1
            data_array = [io.BytesIO() for i in range(num_chunks)]
            tasks = [
                asyncio.ensure_future(
                    self._fetch_range(session, url, i, chunk_size, data_array)
                )
                for i in range(num_chunks)
            ]

            await asyncio.wait(tasks)

            for i in range(num_chunks):
                data_array[i].seek(0)
                data[0].write(data_array[i].read())

    def _run_fetch_large_file(self, loop, url, filesize, data):
        """run async function"""
        loop.run_until_complete(self._fetch_large_file(url, filesize, data))

    def fetch_files(
        self,
        urls,
        filepaths,
        etags=[],
        auto_unzip: bool = True,
    ):
        """fetch multiple files concurrently

        :param urls: the urls to download files from
        :param filepaths: location(s) to keep the files. This can be one path for all files or one path for each file.
        :param etags: old etags. if the old etag is the same with the one on server, do not download again.
        :param auto_unzip: bool flag to indicate if unzip .zip file automatically

        """

        async def f():
            async with aiohttp.ClientSession() as session:
                tasks = []
                for idx, url in enumerate(urls):
                    # get filepath
                    if isinstance(filepaths, str):
                        filepath = filepaths
                    elif isinstance(filepaths, list) and len(filepaths) > idx:
                        filepath = filepaths[idx]
                    else:
                        raise Exception(
                            "The 'filepaths' should be either one string or a list of strings. And the length of the list should be the same with the length of urls. "
                        )

                    # get etag
                    if len(etags) > idx:
                        etag = etags[idx]
                    else:
                        etag = None

                    tasks.append(
                        asyncio.ensure_future(
                            self._fetch_file(
                                session,
                                url,
                                filepath,
                                etag=etag,
                                auto_unzip=auto_unzip,
                            )
                        )
                    )

                return await asyncio.gather(*tasks)

        # set up concurrent functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        new_etags = []
        try:
            new_etags = loop.run_until_complete(f())
            # print(new_etags)
        finally:
            loop.close()
            return new_etags


def fetch_file(
    url: str,
    filepath: str,
    etag: str = None,
    auto_unzip: bool = True,
):
    fetcher = AiohttpFetcher()
    return fetcher.fetch_file(url, filepath, etag=etag, auto_unzip=auto_unzip)


def fetch_files(
    urls,
    filepaths,
    etags=[],
    auto_unzip: bool = True,
):
    fetcher = AiohttpFetcher()
    return fetcher.fetch_files(urls, filepaths, etags=etags, auto_unzip=auto_unzip)


def fetch_large_file(
    url: str,
    filepath: str,
    filesize: int = None,
    etag: str = None,
    auto_unzip: bool = True,
    check_etag: bool = True,
):
    fetcher = AiohttpFetcher()
    return fetcher.fetch_large_file(
        url,
        filepath,
        filesize=filesize,
        etag=etag,
        auto_unzip=auto_unzip,
        check_etag=check_etag,
    )
