import json
import os
import xml.etree.ElementTree as ET

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from rest_framework.decorators import api_view
from utils.model_utils import get_layer_names, get_model_cfg, get_model_name_list


@api_view(["GET"])
def list_model_names(request):
    """List the names of all available retation models"""
    response = HttpResponse(
        json.dumps(get_model_name_list(settings.MODEL_REPO_DIR)),
        content_type="application/json",
    )

    response["Access-Control-Allow-Origin"] = "*"
    return response


@api_view(["GET"])
def get_model_details(request):
    """Given a rotation model name, get details of this model"""

    if request.method == "GET":
        params = request.GET
    else:
        return HttpResponseBadRequest("This method only supports GET requests.")

    model = params.get("model", None)
    if not model:
        return HttpResponseBadRequest("The 'model' parameter is required.")

    try:
        model_cfg = get_model_cfg(model)
    except Exception as e:
        print(e)
        return HttpResponseServerError(f"Unable to find info for model {model}.")

    response = HttpResponse(json.dumps(model_cfg), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


@api_view(["GET"])
def list_model_layers(request):
    """List all available layers for a given plate model"""
    model_name = request.GET.get("model", None)

    if not model_name:
        return HttpResponseBadRequest("The 'model' parameter is required.")

    try:
        layer_names = get_layer_names(model_name)
    except:
        return HttpResponseServerError(f"Unable to find layers for model {model_name}.")

    response = HttpResponse(json.dumps(layer_names), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response
