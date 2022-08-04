import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from utils.get_model import get_reconstruction_model_dict


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

    model_dict = get_reconstruction_model_dict(model)

    if not model_dict:
        return HttpResponseBadRequest(
            'The "model" ({0}) cannot be recognized.'.format(model)
        )

    rotation_model = pygplates.RotationModel(
        [
            f"{settings.MODEL_STORE_DIR}/{model}/{rot_file}"
            for rot_file in model_dict["RotationFile"]
        ]
    )

    static_polygons_filename = (
        f'{settings.MODEL_STORE_DIR}/{model}/{model_dict["StaticPolygons"]}'
    )

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

    pids = [f.get_reconstruction_plate_id() for f in assigned_point_features]
    print(f.get_name() for f in assigned_point_features)

    ret = json.dumps(pids)

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type="application/json")

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
