import json
import logging
import re
from functools import cmp_to_key

from django.conf import settings
from django.http import HttpResponseBadRequest
from rest_framework.decorators import api_view
from utils.decorators import return_HttpResponse
from utils.plate_model_utils import get_layer_names, get_model_cfg, get_model_name_list

PUBLIC_MODELS = [
    "CAO2024",
    "ALFONSO2024",
    "MULLER2022",
    "ZAHIROVIC2022",
    "MERDITH2021",
    "CLENNETT2020",
    "MULLER2019",
    "MULLER2016",
    "MATTHEWS2016_mantle_ref",
    "MATTHEWS2016_pmag_ref",
    "SETON2012",
    "GOLONKA",
    "PALEOMAP",
    "TorsvikCocks2017",
    "RODINIA",
]
logger = logging.getLogger("default")


def _compare(first, second):
    first_numbers = re.findall(r"\d+", first)
    second_numbers = re.findall(r"\d+", second)
    if not first_numbers:
        first_numbers = [0]
    if not second_numbers:
        second_numbers = [0]

    if int(first_numbers[0]) > int(second_numbers[0]):
        return -1

    if int(first_numbers[0]) == int(second_numbers[0]):
        return 1 if first > second else -1

    return 1


@api_view(["GET"])
@return_HttpResponse()
def list_model_names(request):
    """HTTP request handler for /model/list
    return a list of public available rotation model names"""
    if request.method != "GET":
        return HttpResponseBadRequest(
            "Only HTTP GET request is supported for this endpoint."
        )
    ret = []
    available_models = get_model_name_list(settings.MODEL_REPO_DIR)
    for model_name in available_models:
        if model_name.lower() in map(str.lower, PUBLIC_MODELS):
            ret.append(model_name)
    return json.dumps(sorted(ret, key=cmp_to_key(_compare)))


@api_view(["GET"])
@return_HttpResponse()
def get_model_details(request):
    """HTTP request handler for /model/show
    return details for a given rotation model name"""

    # TODO decorator
    if request.method != "GET":
        return HttpResponseBadRequest(
            "Only HTTP GET request is supported for this endpoint."
        )

    # TODO decorator
    model = request.GET.get("model", None)
    if not model:
        return HttpResponseBadRequest(
            "The 'model' parameter is required. Use https://gws.gplates.org/model/list to get a list of available models."
        )

    try:
        model_cfg = get_model_cfg(model)
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(
            f"Unable to find info for model {model}. Use https://gws.gplates.org/model/list to get a list of available models."
        )

    return json.dumps(model_cfg)


@api_view(["GET"])
@return_HttpResponse()
def list_model_layers(request):
    """HTTP request handler for /model/list_layers
    return all available layers for a given plate model"""
    if request.method != "GET":
        return HttpResponseBadRequest(
            "Only HTTP GET request is supported for this endpoint."
        )

    model = request.GET.get("model", None)
    if not model:
        return HttpResponseBadRequest(
            "The 'model' parameter is required. Use https://gws.gplates.org/model/list to get a list of available models."
        )

    try:
        layer_names = get_layer_names(model)
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(
            f"Unable to find info for model {model}. Use https://gws.gplates.org/model/list to get a list of available models."
        )

    return json.dumps(layer_names)


def download_model():
    # TODO
    pass
