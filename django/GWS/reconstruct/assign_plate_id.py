import json
import math

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from utils.geojson_io import load_geojson
from utils.parameter_helper import get_lats_lons
from utils.plate_model_utils import get_rotation_model, get_static_polygons
from utils.reconstruct_tools import assign_plate_ids


@csrf_exempt
def get_points_pids(request):
    """
    assign plate IDs to locations/points
    http://localhost:18000/reconstruct/assign_points_plate_ids?lons=-10,-130,0&lats=50,-70,0
    http://localhost:18000/reconstruct/assign_points_plate_ids?points=-10,50,-130,-70,0,0&with_valid_time
    """
    if request.method == "POST":
        params = request.POST
    elif request.method == "GET":
        params = request.GET
    else:
        return HttpResponseBadRequest(
            "Unrecognized request type. Only accept POST and GET requests."
        )

    model = params.get("model", settings.MODEL_DEFAULT)
    with_valid_time = True if "with_valid_time" in params else False

    # create point features from input coordinates
    lats, lons = get_lats_lons(params)
    geoms = [pygplates.PointOnSphere(lat, lon) for lat, lon in zip(lats, lons)]

    pids_and_times = assign_plate_ids(geoms, model)

    if with_valid_time:
        pid_valid_time_list = []

        for x in pids_and_times:
            begin_time = x[1]
            end_time = x[2]

            if math.isinf(begin_time):
                begin_time = "distant past"
            if math.isinf(end_time):
                end_time = "distant future"
            pid_valid_time_list.append(
                {"pid": x[0], "valid_time": [begin_time, end_time]}
            )
        ret = json.dumps(pid_valid_time_list)
    else:
        ret = json.dumps([x[0] for x in pids_and_times])

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type="application/json")

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response


#
# reconstruct geojson features plate IDs
#
@csrf_exempt
def get_plate_ids_for_geojson(request):
    if request.method == "POST":
        params = request.POST
    elif request.method == "GET":
        params = request.GET
    else:
        return HttpResponseBadRequest(
            "Unrecognized request type. Only accept POST and GET requests."
        )

    fc_str = params.get("feature_collection")
    model = str(params.get("model", settings.MODEL_DEFAULT))

    # Convert geojson input to gplates feature collection
    feature_collection = load_geojson(fc_str, False)

    rotation_model = get_rotation_model(model)

    assigned_features = pygplates.partition_into_plates(
        get_static_polygons(model),
        rotation_model,
        feature_collection,
        properties_to_copy=[
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period,
        ],
        partition_method=pygplates.PartitionMethod.most_overlapping_plate,
    )

    assert len(feature_collection) == len(assigned_features)

    pids_dict = dict(
        (f.get_name(), f.get_reconstruction_plate_id()) for f in assigned_features
    )
    # print(f.get_name() for f in assigned_features)

    pids = []
    for i in range(
        0, len(assigned_features)
    ):  # make sure the order of features is correct
        pids.append(pids_dict[str(i)])

    ret = json.dumps(pids)

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
