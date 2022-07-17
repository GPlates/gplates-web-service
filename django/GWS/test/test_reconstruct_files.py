# open this script in vs code
# connect to gplates web service docker container
# run it inside vs code
import os
from pathlib import Path

import requests

url = "http://localhost:80/reconstruct/reconstruct_files"
# url = "http://localhost:18000/reconstruct/reconstruct_files"
# url = 'https://gws.gplates.org/reconstruct/reconstruct_files'

script_path = os.path.dirname(os.path.realpath(__file__))
# print(script_path)
output_path = f"{script_path}/output"
Path(output_path).mkdir(parents=True, exist_ok=True)

files = {
    "file_1": open(f"{script_path}/Australia_Points.shx", "rb"),
    "file_2": open(f"{script_path}/Australia_Points.prj", "rb"),
    "file_3": open(f"{script_path}/Australia_Points.shp", "rb"),
    "file_4": open(f"{script_path}/Australia_Points.dbf", "rb"),
}

data = {"time": 100}

r = requests.post(url, files=files, data=data)
print(r.reason)

with open(f"{script_path}/result.zip", "wb") as of:
    of.write(r.content)

print("done!")
