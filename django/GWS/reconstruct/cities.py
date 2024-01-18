import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from utils.plate_model_utils import get_rotation_model, get_static_polygons
from utils.round_float import round_floats

cities_lon_lat = {
    "Sydney": [151.2099, -33.8651],
    "Melbourne": [144.9465, -37.8409],
    "Perth": [115.8613, -31.9523],
    "Darwin": [130.8444, -12.4637],
    "Adelaide": [138.6007, -34.9285],
}


def get_city_lon_lat_at_time(request):
    time = request.GET.get("time", None)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    timef = 0.0
    if not time:
        return HttpResponseBadRequest('The "time" parameter cannot be empty.')
    else:
        try:
            timef = float(time)
        except:
            return HttpResponseBadRequest(
                'The "time" parameter is invalid ({0}).'.format(time)
            )

    rotation_model = get_rotation_model(model)

    # create features
    point_features = []
    for key in cities_lon_lat:
        point_feature = pygplates.Feature()
        point_feature.set_geometry(
            pygplates.PointOnSphere(cities_lon_lat[key][1], cities_lon_lat[key][0])
        )
        point_feature.set_name(key)
        point_features.append(point_feature)

    # assign plate ids
    assigned_point_features = pygplates.partition_into_plates(
        get_static_polygons(model),
        rotation_model,
        point_features,
        properties_to_copy=[
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period,
        ],
    )

    # reconstruct
    reconstructed_feature_geometries = []
    pygplates.reconstruct(
        assigned_point_features,
        rotation_model,
        reconstructed_feature_geometries,
        timef,
    )

    ret = {"type": "FeatureCollection", "features": []}
    for rfg in reconstructed_feature_geometries:
        feat = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    rfg.get_reconstructed_geometry().to_lat_lon()[1],
                    rfg.get_reconstructed_geometry().to_lat_lon()[0],
                ],
            },
            "properties": {"name": rfg.get_feature().get_name()},
        }
        ret["features"].append(feat)

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(
        json.dumps(round_floats(ret)), content_type="application/json"
    )

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
