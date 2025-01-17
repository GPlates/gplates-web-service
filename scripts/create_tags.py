#!/usr/bin/env python3
import os
import subprocess
import sys

if len(sys.argv) != 2:
    print("Usage: ./create-tag.py VERSION(such as 1.1.0)")
    sys.exit(1)

new_version = sys.argv[1]

this_file_path = os.path.dirname(__file__)

# 1. update version number in django/GWS/GWS/version.py
# 2. commit change, create a tag and push changes and the new tag

lines = []
with open(f"{this_file_path}/../django/GWS/GWS/version.py", "r") as f:
    for line in f:
        if line.startswith("VERSION"):
            lines.append(f'VERSION = "{new_version}"\n')
        else:
            lines.append(line)

with open(f"{this_file_path}/../django/GWS/GWS/version.py", "w") as of:
    of.writelines(lines)

subprocess.call(["git", "add", f"{this_file_path}/../django/GWS/GWS/version.py"])

files = [
    f"{this_file_path}/../docker/Dockerfile",
    f"{this_file_path}/../docker/postgis/Dockerfile",
]

for file in files:
    lines = []
    with open(file, "r") as f:
        for line in f:
            items = line.split(" ")
            if (
                len(items) > 1
                and items[0].strip().lower() == "label"
                and items[1].strip().lower().startswith("version")
            ):
                lines.append(f'LABEL version="{new_version}"\n')
            else:
                lines.append(line)

    with open(file, "w") as of:
        of.writelines(lines)
    subprocess.call(["git", "add", file])


subprocess.call(["git", "commit", "-m", f"update version to {new_version}"])
subprocess.call(["git", "push"])

if not new_version.startswith("v"):
    new_version = "v" + new_version
subprocess.call(["git", "tag", new_version])
subprocess.call(["git", "push", "origin", "--tags"])
