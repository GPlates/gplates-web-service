import json

import pygplates
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from utils.model_utils import get_rotation_model, get_topologies
from utils.round_float import round_floats
from utils.wrapping_tools import wrap_plate_boundaries, wrap_resolved_polygons


def get_plate_polygons(request):
    """
    http GET request to retrieve reconstructed topological plate polygons

    **usage**

    <http-address-to-gws>/topology/plate_polygons/time=\ *reconstruction_time*\&model=\ *reconstruction_model*

    **parameters:**

    *time* : time for reconstruction [default=0]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    **returns:**

    json containing reconstructed plate polygon features
    """

    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    wrap_to_dateline = request.GET.get("wrap_to_dateline", True)

    resolved_polygons = []
    pygplates.resolve_topologies(
        get_topologies(model), get_rotation_model(model), resolved_polygons, float(time)
    )

    resolved_features = []
    for polygon in resolved_polygons:
        resolved_features.append(polygon.get_resolved_feature())

    data = wrap_resolved_polygons(resolved_features, wrap=wrap_to_dateline)

    ret = json.dumps(round_floats(data))

    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_topological_boundaries(request):
    """
    http GET request to retrieve reconstructed topological plate polygons

    **usage**

    <http-address-to-gws>/topology/plate_boundaries/time=\ *reconstruction_time*\&model=\ *reconstruction_model*

    **parameters:**

    *time* : time for reconstruction [default=0]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    **returns:**

    json containing reconstructed plate boundary features
    """

    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    print(get_topologies(model))
    print(get_rotation_model(model))

    resolved_polygons = []
    shared_boundary_sections = []
    pygplates.resolve_topologies(
        get_topologies(model),
        get_rotation_model(model),
        resolved_polygons,
        float(time),
        shared_boundary_sections,
    )

    data = wrap_plate_boundaries(shared_boundary_sections, 0.0)

    ret = json.dumps(round_floats(data))

    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
