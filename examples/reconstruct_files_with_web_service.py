# open this script in vs code
# connect to gplates web service docker container
# run it inside vs code
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

SERVER_URL = os.getenv("GWS_SERVER_URL")
if not SERVER_URL:
    SERVER_URL = "https://gws.gplates.org"
    # SERVER_URL = "http://localhost:18000"
    print(f"Using server URL in script {SERVER_URL}")
else:
    print(f"Using server URL in environment variable {SERVER_URL}")

url = f"{SERVER_URL}/reconstruct/reconstruct_files"

script_path = os.path.dirname(os.path.realpath(__file__))
# print(script_path)
output_path = f"{script_path}/output"
Path(output_path).mkdir(parents=True, exist_ok=True)

load_dotenv(f"{script_path}/.env")  # take environment variables from .env.

data_folder = f"{script_path}/data"
files = {
    "file_1": open(f"{data_folder}/Australia_Points.shx", "rb"),
    "file_2": open(f"{data_folder}/Australia_Points.prj", "rb"),
    "file_3": open(f"{data_folder}/Australia_Points.shp", "rb"),
    "file_4": open(f"{data_folder}/Australia_Points.dbf", "rb"),
}

# You may compress the shapefiles into a zip file and use the line below
# files = {"file_1": open(f"{data_folder}/Australia_Points.zip", "rb")}

data = {
    "time": 100,
    # "model": "MULLER2019",
    "assign_plate_id": 1,  # set to 0, if your files already contains plate ids. the save_plate_id parameter will override this parameter
    "basename": "my-reconstructed-file",  # your preferred output file name
    "save_plate_id": 0,  # save the intermedia files with assigned plate ids. This parameter will be no effect if you choose to upload the result to geoserver.
    # uncomment the following parameters to upload result file to geoserver
    # "geosrv_url": os.getenv("GEOSRV_URL"),
    # "geosrv_username": os.getenv("GEOSRV_USERNAME"),
    # "geosrv_password": os.getenv("GEOSRV_PASSWORD"),
    # "geosrv_workspace": "test-web-service-upload-workspace",
}

r = requests.post(url, files=files, data=data)
print(r.reason)

with open(f"{output_path}/result.zip", "wb") as of:
    of.write(r.content)

print("done!")
