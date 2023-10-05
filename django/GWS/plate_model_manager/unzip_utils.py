import bz2
import gzip
import lzma
import shutil
import tarfile
import zipfile

from . import misc_utils


def save_compressed_data(url, data, dst_path):
    """extract files from compressed data

    :param url: URL
    :param data: bytes-like object
    :param dst_path: location to save the files
    """
    # print(f"save_compressed_data:{url}")
    # .zip
    if url.endswith(".zip"):
        if not zipfile.is_zipfile(data):
            misc_utils.print_warning(
                f"The {url} seems a zip file. But it is in fact not. Will not decompress the file."
            )
            raise Exception("Bad compressed data!")
        else:
            with zipfile.ZipFile(data) as z:
                z.extractall(dst_path)
                z.close()
    # .tar.gz or .tgz
    elif url.endswith(".tar.gz") or url.endswith(".tgz"):
        if not tarfile.is_tarfile(data):
            misc_utils.print_warning(
                f"The {url} seems a tar gzip file. But it is in fact not. Will not decompress the file."
            )
            raise Exception("Bad compressed data!")
        else:
            with tarfile.open(fileobj=data, mode="r:gz") as tar:
                tar.extractall(path=dst_path)
                tar.close()
    # .gz
    elif url.endswith(".gz"):
        try:
            fn = url.split("/")[-1][:-3]
            with open(f"{dst_path}/{fn}", "wb+") as f_out:
                with gzip.GzipFile(fileobj=data) as f_in:
                    shutil.copyfileobj(f_in, f_out)
                    f_in.close()
                f_out.close()
        except:
            misc_utils.print_warning(
                f"The {url} seems a gzip file. But it is in fact not. Will not decompress the file."
            )
            raise Exception("Bad compressed data!")
    # .tar.bz2 or .tbz2
    elif url.endswith(".tar.bz2") or url.endswith(".tbz2"):
        if not tarfile.is_tarfile(data):
            misc_utils.print_warning(
                f"The {url} seems a tar bz2 file. But it is in fact not. Will not decompress the file."
            )
            raise Exception("Bad compressed data!")
        else:
            with tarfile.open(fileobj=data, mode="r:bz2") as tar:
                tar.extractall(path=dst_path)
                tar.close()
    # .bz2
    elif url.endswith(".bz2"):
        try:
            fn = url.split("/")[-1][:-4]
            with open(f"{dst_path}/{fn}", "wb+") as f_out:
                data = bz2.decompress(data.read())
                f_out.write(data)
                f_out.close()
        except:
            misc_utils.print_warning(
                f"The {url} seems a bz2 file. But it is in fact not. Will not decompress the file."
            )
            raise Exception("Bad compressed data!")
    # .lzma
    elif url.endswith(".lzma"):
        try:
            fn = url.split("/")[-1][:-5]
            with open(f"{dst_path}/{fn}", "wb+") as f_out:
                data = lzma.decompress(data.read())
                f_out.write(data)
                f_out.close()
        except:
            misc_utils.print_warning(
                f"The {url} seems a lzma file. But it is in fact not. Will not decompress the file."
            )
            raise Exception("Bad compressed data!")
    # .tar.xz or .txz
    elif url.endswith(".tar.xz") or url.endswith(".txz"):
        if not tarfile.is_tarfile(data):
            misc_utils.print_warning(
                f"The {url} seems a tar xz file. But it is in fact not. Will not decompress the file."
            )
            raise Exception("Bad compressed data!")
        else:
            with tarfile.open(fileobj=data, mode="r:xz") as tar:
                tar.extractall(path=dst_path)
                tar.close()
    # .xz
    elif url.endswith(".xz"):
        try:
            fn = url.split("/")[-1][:-3]
            with open(f"{dst_path}/{fn}", "wb+") as f_out:
                data = lzma.decompress(data.read())
                f_out.write(data)
                f_out.close()
        except:
            misc_utils.print_warning(
                f"The {url} seems a xz file. But it is in fact not. Will not decompress the file."
            )
            raise Exception("Bad compressed data!")
    else:
        raise Exception("Unrecognized zip data!")
