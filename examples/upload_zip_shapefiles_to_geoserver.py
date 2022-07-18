# open this script in vs code
# connect to gplates web service docker container
# run it inside vs code

import os

from dotenv import load_dotenv
from geo.Geoserver import Geoserver

script_path = os.path.dirname(os.path.realpath(__file__))

load_dotenv(f"{script_path}/.env")  # take environment variables from .env.

geo = Geoserver(
    os.getenv("GEOSRV_URL"),
    username=os.getenv("GEOSRV_USERNAME"),
    password=os.getenv("GEOSRV_PASSWORD"),
)
geo.create_workspace(workspace="test-upload-zip-shapefiles")
geo.create_shp_datastore(
    path=f"{script_path}/output/result.zip",  # make sure you have this zip file
    store_name="reconstructed-100Ma",  # the shapefiles basename
    workspace="test-upload-zip-shapefiles",
)
