import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from utils.geojson_io import load_geojson, save_reconstructed_geometries_geojson
from utils.model_utils import get_rotation_model, get_static_polygons_filename
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

    anchor_plate_id = params.get("pid", 0)

    if "time" in params:
        time = params["time"]
    elif "geologicage" in params:
        time = params["geologicage"]
    else:
        time = 140  # default reconstruction age

    # output_format = params.get("output", "geojson")
    fc_str = params.get("feature_collection")
    model = str(params.get("model", settings.MODEL_DEFAULT))

    if "keep_properties" in params:
        keep_properties = True
    else:
        keep_properties = False

    try:
        timef = float(time)
    except:
        return HttpResponseBadRequest(
            'The "time" parameter is invalid ({0}).'.format(time)
        )

    try:
        anchor_plate_id = int(anchor_plate_id)
    except:
        return HttpResponseBadRequest(
            'The "pid" parameter is invalid ({0}).'.format(anchor_plate_id)
        )

    # Convert geojson input to gplates feature collection
    feature_collection = load_geojson(fc_str, keep_properties)

    rotation_model = get_rotation_model(model)
    static_polygons_filename = get_static_polygons_filename(model)

    assigned_features = pygplates.partition_into_plates(
        static_polygons_filename,
        rotation_model,
        feature_collection,
        properties_to_copy=[
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period,
        ],
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
