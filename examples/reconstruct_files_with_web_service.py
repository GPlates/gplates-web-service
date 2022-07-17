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

data_folder = f"{script_path}/data"
files = {
    "file_1": open(f"{data_folder}/Australia_Points.shx", "rb"),
    "file_2": open(f"{data_folder}/Australia_Points.prj", "rb"),
    "file_3": open(f"{data_folder}/Australia_Points.shp", "rb"),
    "file_4": open(f"{data_folder}/Australia_Points.dbf", "rb"),
}

# You may compess the shapefiles into a zip file and use the line below
# files = {"file_1": open(f"{data_folder}/Australia_Points.zip", "rb")}

data = {"time": 100}

r = requests.post(url, files=files, data=data)
print(r.reason)

with open(f"{output_path}/result.zip", "wb") as of:
    of.write(r.content)

print("done!")
