import json

import pygplates
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from utils.decorators import extract_params, return_HttpResponse
from utils.geojson_io import load_geojson
from utils.parameter_helper import get_bool, get_lats_lons
from utils.reconstruct_tools import assign_plate_ids


def _prepare_ret(pids_and_times, with_valid_time):
    if with_valid_time:
        pid_valid_time_list = []

        for x in pids_and_times:
            begin_time = x[1]
            end_time = x[2]

            if begin_time is None:
                begin_time = "distant past"
            if end_time is None:
                end_time = "distant future"
            pid_valid_time_list.append(
                {"pid": x[0], "valid_time": [begin_time, end_time]}
            )
        return json.dumps(pid_valid_time_list)
    else:
        return json.dumps([x[0] for x in pids_and_times])


@csrf_exempt
@extract_params
@return_HttpResponse()
def get_points_pids(request, params={}):
    """http request handler for reconstruct/assign_points_plate_ids
    return a list of plate IDs for the input locations/points

    http://localhost:18000/reconstruct/assign_points_plate_ids?lons=-10,-130,0&lats=50,-70,0
    http://localhost:18000/reconstruct/assign_points_plate_ids?points=-10,50,-130,-70,0,0&with_valid_time=true
    """

    model = params.get("model", settings.MODEL_DEFAULT)
    with_valid_time = get_bool(params, "with_valid_time", False)

    # create point features from input coordinates
    lats, lons = get_lats_lons(params)
    geoms = [pygplates.PointOnSphere(lat, lon) for lat, lon in zip(lats, lons)]

    pids_and_times = assign_plate_ids(geoms, model)

    return _prepare_ret(pids_and_times, with_valid_time)


@csrf_exempt
@extract_params
@return_HttpResponse()
def get_plate_ids_for_geojson(request, params={}):
    """http request handler for /reconstruct/assign_geojson_plate_ids
    return a list of plate IDs for the given feature collection in geojson format

    http://localhost:18000/reconstruct/assign_geojson_plate_ids

    """
    fc_str = params.get("feature_collection", "")
    model = params.get("model", settings.MODEL_DEFAULT)
    with_valid_time = get_bool(params, "with_valid_time", False)

    # Convert geojson input to gplates feature collection
    try:
        feature_collection = load_geojson(fc_str, False)
    except:
        return HttpResponseBadRequest("Unable to load feature collection.")

    # geojson supports only one geometry per feature
    geoms = [f.get_geometry() for f in feature_collection]

    pids_and_times = assign_plate_ids(geoms, model)

    return _prepare_ret(pids_and_times, with_valid_time)
