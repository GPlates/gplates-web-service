import os

from django.conf import settings
from django.http import HttpResponse

script_path = os.path.dirname(os.path.realpath(__file__))
data_path = f"{settings.BASE_DIR}/DATA/mobile-app/"


def get_layers(request):
    '''
    get vector layers for a given raster ID.
    if the vector layers do not exist, return the default ones.
    '''
    raster_id = request.GET.get("raster", None)

    cfg_file = f"{data_path}/{raster_id}-vector-layers.json"
    if not os.path.isfile(cfg_file):
        cfg_file = f"{data_path}/default-vector-layers.json"

    with open(cfg_file, "r") as f:
        response = HttpResponse(
            f, content_type="application/json; charset=utf8")
        response["Access-Control-Allow-Origin"] = "*"
        return response
