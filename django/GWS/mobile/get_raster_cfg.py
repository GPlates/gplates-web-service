import json
import os
import base64

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

script_path = os.path.dirname(os.path.realpath(__file__))

#
# get raster configurations as json
#
def get_rasters(request):
    with open(f"{script_path}/raster_cfg.json") as f:
        data = json.load(f)
        for key in data:
            with open(f"{script_path}/{data[key]['icon']}", "rb") as image_file:
                base64_code = base64.b64encode(image_file.read())
                data[key]["icon"] = base64_code.decode("utf-8")
        # print(data)
        response = HttpResponse(json.dumps(data), content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        return response
