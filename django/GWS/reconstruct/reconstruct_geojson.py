import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from utils.geojson_io import load_geojson, save_reconstructed_geometries_geojson
from utils.parameter_helper import get_anchor_plate_id, get_time
from utils.plate_model_utils import (
    UnrecognizedModel,
    get_rotation_model,
    get_static_polygons,
)
from utils.round_float import round_floats


#
# reconstruct geojson feature collection
#
@csrf_exempt
def reconstruct(request):
    if request.method == "POST":
        params = request.POST
    elif request.method == "GET":
        params = request.GET
    else:
        return HttpResponseBadRequest("Unrecognized request type")

    # output_format = params.get("output", "geojson")
    fc_str = params.get("feature_collection")
    model = params.get("model", settings.MODEL_DEFAULT)

    ignore_valid_time = True if "ignore_valid_time" in params else False
    keep_properties = True if "keep_properties" in params else False

    if "time" not in params and "geologicage" in params:
        timef = get_time(params, name="geologicage")
    else:
        timef = get_time(params)
    anchor_plate_id = get_anchor_plate_id(params)

    # Convert geojson input to gplates feature collection
    feature_collection = load_geojson(fc_str, keep_properties)

    try:
        rotation_model = get_rotation_model(model)
    except UnrecognizedModel as e:
        return HttpResponseBadRequest(
            f"""Unrecognized Rotation Model: {model}.<br>
            Use <a href="https://gws.gplates.org/info/model_names">https://gws.gplates.org/info/model_names</a>
            to find all available models."""
        )

    properties_to_copy = [pygplates.PartitionProperty.reconstruction_plate_id]
    if not ignore_valid_time:
        properties_to_copy.append(pygplates.PartitionProperty.valid_time_period)

    assigned_features = pygplates.partition_into_plates(
        get_static_polygons(model),
        rotation_model,
        feature_collection,
        properties_to_copy=properties_to_copy,
        partition_method=pygplates.PartitionMethod.most_overlapping_plate,
    )

    reconstructed_geometries = []
    pygplates.reconstruct(
        assigned_features,
        rotation_model,
        reconstructed_geometries,
        timef,
        anchor_plate_id=anchor_plate_id,
    )

    # convert feature collection back to geojson
    data = save_reconstructed_geometries_geojson(
        reconstructed_geometries, keep_properties
    )

    ret = json.dumps(round_floats(data))

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
