import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from utils.model_utils import (
    get_rotation_model,
    get_static_polygons_filename,
)
from utils.geojson_io import load_geojson


#
# assign plate IDs to locations/points
#
@csrf_exempt
def get_points_pids(request):
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

    rotation_model = get_rotation_model(model)
    static_polygons_filename = get_static_polygons_filename(model)

    # create point features from input coordinates
    # filter out invalid characters
    points = "".join(c for c in points if c.isdecimal() or (c in [".", ","]))
    p_index = 0
    point_features = []
    if points:
        ps = points.split(",")
        ps_len = len(ps)
        if ps_len % 2 == 0:
            try:
                for lat, lon in zip(ps[1::2], ps[0::2]):
                    point_feature = pygplates.Feature()
                    point_feature.set_geometry(
                        pygplates.PointOnSphere(float(lat), float(lon))
                    )
                    point_feature.set_name(str(p_index))
                    point_features.append(point_feature)
                    p_index += 1
            except pygplates.InvalidLatLonError as e:
                return HttpResponseBadRequest(
                    "Invalid longitude or latitude ({0}).".format(e)
                )
            except ValueError as e:
                return HttpResponseBadRequest("Invalid value ({0}).".format(e))
        else:
            return HttpResponseBadRequest(
                "The longitude and latitude should come in pairs ({0}).".format(points)
            )
    else:
        return HttpResponseBadRequest('The "points" parameter is missing.')

    # assign plate-ids to points using static polygons
    assigned_point_features = pygplates.partition_into_plates(
        static_polygons_filename,
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
