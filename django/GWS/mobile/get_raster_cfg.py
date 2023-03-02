import base64
import json
import os

from django.conf import settings
from django.http import HttpResponse

script_path = os.path.dirname(os.path.realpath(__file__))
data_path = f"{settings.BASE_DIR}/DATA/mobile-app/"

#
# get raster configurations as json
#


def get_rasters(request):
    with open(f"{data_path}/raster-cfg.json", "r") as f:
        data = json.load(f)
        for key in data:
            with open(f"{data_path}/{data[key]['icon']}", "rb") as image_file:
                base64_code = base64.b64encode(image_file.read())
                data[key]["icon"] = base64_code.decode("utf-8")
        # print(data)
        response = HttpResponse(json.dumps(
            data), content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        return response
