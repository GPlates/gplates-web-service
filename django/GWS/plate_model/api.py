import io
import json
import logging
import os
import zipfile

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, schema
from rest_framework.schemas.openapi import AutoSchema
from utils.decorators import (
    extract_model_required,
    extract_params_GET_only,
    return_HttpResponse,
)
from utils.plate_model_utils import (
    get_layer_names,
    get_model_cfg,
    get_model_dir,
    get_model_name_list,
)

logger = logging.getLogger("default")


class PlateModelSchema(AutoSchema):

    def get_operation_id(self, path, method):
        return path + str(method)


@api_view(["GET"])
@schema(PlateModelSchema())
@extract_params_GET_only
@return_HttpResponse()
def list_model_names(_, **kwags):
    """HTTP request handler for /model/list

    http://localhost:18000/model/list

    Return a list of public available rotation model names.
    The list will be sorted by publish year first and then alphabet order."""

    return json.dumps(get_model_name_list(settings.MODEL_REPO_DIR))


@api_view(["GET"])
@schema(PlateModelSchema())
@extract_params_GET_only
@extract_model_required
@return_HttpResponse()
def get_model_details(_, model="", **kwags):
    """HTTP request handler for /model/show

    http://localhost:18000/model/show?model=muller2019

    return details for a given rotation model name"""

    try:
        model_cfg = get_model_cfg(model)
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(
            f"Unable to find info for model {model}."
            + ' Use <a href="https://gws.gplates.org/model/list">https://gws.gplates.org/model/list</a> to get the list of available model names.'
        )

    return json.dumps(model_cfg)


@api_view(["GET"])
@schema(PlateModelSchema())
@extract_params_GET_only
@extract_model_required
@return_HttpResponse()
def list_model_layers(_, model="", **kwags):
    """HTTP request handler for /model/list_layers

    http://localhost:18000/model/list_layers?model=muller2019

    return all available layers for a given plate model"""
    try:
        layer_names = get_layer_names(model)
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(
            f"Unable to list layers for model {model}."
            + ' Use <a href="https://gws.gplates.org/model/list">https://gws.gplates.org/model/list</a> to get the list of supported model names.'
        )

    return json.dumps(layer_names)


@api_view(["GET"])
@schema(PlateModelSchema())
@extract_params_GET_only
@extract_model_required
def download_model(_, model="", **kwags):
    """HTTP request handler for /model/download

    http://localhost:18000/model/download?model=muller2019

    Return the model files in a .zip file."""

    model_dir = get_model_dir(model, settings.MODEL_REPO_DIR)
    s = io.BytesIO()
    with zipfile.ZipFile(s, "w") as zf:
        for root, dirs, files in os.walk(model_dir):
            for file in files:
                zf.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file),
                        os.path.join(model_dir, ".."),
                    ),
                )

    response = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    response["Content-Disposition"] = f"attachment; filename={model}.zip"
    response["Access-Control-Allow-Origin"] = "*"
    return response
