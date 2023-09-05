import sys

from .plate_model import *
from .plate_model_manager import PlateModelManager

import argparse


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

    download_cmd.add_argument("model", type=str)
    download_cmd.add_argument("path", type=str, nargs="?", default=os.getcwd())

    download_cmd.add_argument("-r", "--repository", type=str, dest="repository")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "ls":
        if args.repository == None:
            pm_manager = PlateModelManager()
        else:
            pm_manager = PlateModelManager(args.repository)
        for name in pm_manager.get_available_model_names():
            print(name)
    elif args.command == "download":
        print(f"download {args.model}")
        if args.repository == None:
            pm_manager = PlateModelManager()
        else:
            pm_manager = PlateModelManager(args.repository)

        if args.model.lower() == "all":
            pm_manager.download_all_models(args.path)
        else:
            model = pm_manager.get_model(args.model)
            model.set_data_dir(args.path)
            model.download_all_layers()


if __name__ == "__main__":
    main()
