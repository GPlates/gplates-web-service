import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from utils.model_utils import (
    get_rotation_model,
    get_static_polygons,
    UnrecognizedModel,
)
from utils.geojson_io import load_geojson
from utils.get_lats_lons import get_lats_lons


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

    points = params.get("points", None)
    model = params.get("model", settings.MODEL_DEFAULT)
    with_valid_time = True if "with_valid_time" in params else False

    try:
        rotation_model = get_rotation_model(model)
    except UnrecognizedModel as e:
        return HttpResponseBadRequest(
            f"""Unrecognized Rotation Model: {model}.<br>
        Use <a href="https://gws.gplates.org/info/model_names">https://gws.gplates.org/info/model_names</a>
        to find all available models."""
        )

    # create point features from input coordinates
    p_index = 0
    point_features = []
    lats, lons = get_lats_lons(params)

    try:
        for lat, lon in zip(lats, lons):
            point_feature = pygplates.Feature()
            point_feature.set_geometry(pygplates.PointOnSphere(float(lat), float(lon)))
            point_feature.set_name(str(p_index))
            point_features.append(point_feature)
            p_index += 1
    except pygplates.InvalidLatLonError as e:
        return HttpResponseBadRequest("Invalid longitude or latitude ({0}).".format(e))
    except ValueError as e:
        return HttpResponseBadRequest("Invalid value ({0}).".format(e))

    # assign plate-ids to points using static polygons
    assigned_point_features = pygplates.partition_into_plates(
        get_static_polygons(model),
        rotation_model,
        point_features,
        properties_to_copy=[
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period,
        ],
        reconstruction_time=0.0,
    )

    assert len(point_features) == len(assigned_point_features)

    pids_dict = dict(
        (f.get_name(), f.get_reconstruction_plate_id()) for f in assigned_point_features
    )
    # print(f.get_name() for f in assigned_point_features)

    pids = []
    for i in range(
        0, len(assigned_point_features)
    ):  # make sure the order of features is correct
        pids.append(pids_dict[str(i)])

    if with_valid_time:
        pid_valid_time_list = []
        valid_time_dict = dict(
            (f.get_name(), f.get_valid_time(None)) for f in assigned_point_features
        )

        for i in range(0, len(assigned_point_features)):
            pid = pids_dict[str(i)]
            valid_time = valid_time_dict[str(i)]
            if valid_time:
                begin_time, end_time = valid_time
            else:
                begin_time = None
                end_time = None
            if begin_time == pygplates.GeoTimeInstant.create_distant_past():
                begin_time = "distant past"
            if end_time == pygplates.GeoTimeInstant.create_distant_future():
                end_time = "distant future"
            pid_valid_time_list.append(
                {"pid": pid, "valid_time": [begin_time, end_time]}
            )
        ret = json.dumps(pid_valid_time_list)
    else:
        ret = json.dumps(pids)

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
