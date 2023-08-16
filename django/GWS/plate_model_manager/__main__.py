import sys

from .plate_model import *
from .plate_model_manager import PlateModelManager

import argparse

DEFAULT_REPO_URL = "https://www.earthbyte.org/webdav/ftp/plate-model-repo/models.json"


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"error: {message}\n")
        self.print_help()
        sys.exit(1)


def main():
    parser = ArgParser()

    subparser = parser.add_subparsers(dest="command")
    ls_cmd = subparser.add_parser("ls")
    download_cmd = subparser.add_parser("download")

    ls_cmd.add_argument("-r", "--repository", type=str, dest="repository")

    download_cmd.add_argument("-m", "--model", type=str, dest="model", required=True)
    download_cmd.add_argument("-p", "--path", type=str, dest="path", default="./")
    download_cmd.add_argument("-r", "--repository", type=str, dest="repository")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "ls":
        if args.repository == None:
            pm_manager = PlateModelManager(DEFAULT_REPO_URL)
        else:
            pm_manager = PlateModelManager(args.repository)
        print(pm_manager.get_available_model_names())
    elif args.command == "download":
        print(f"download {args.model}")
        if args.repository == None:
            pm_manager = PlateModelManager(DEFAULT_REPO_URL)
        else:
            pm_manager = PlateModelManager(args.repository)
        model = pm_manager.get_model(args.model)
        model.set_data_dir(args.path)
        model.download_all()


if __name__ == "__main__":
    main()
