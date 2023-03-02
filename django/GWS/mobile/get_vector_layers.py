import os

from django.conf import settings
from django.http import HttpResponse

script_path = os.path.dirname(os.path.realpath(__file__))
data_path = f"{settings.BASE_DIR}/DATA/mobile-app/"


def get_layers(request):
    '''get vector layers for a given model'''
    model_name = request.GET.get("model", "SETON2012")
    with open(f"{data_path}/{model_name}-layers.json", "r") as f:
        response = HttpResponse(
            f, content_type="application/json; charset=utf8")
        response["Access-Control-Allow-Origin"] = "*"
        return response
