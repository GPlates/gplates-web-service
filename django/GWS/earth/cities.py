import json
import math

import pygplates
from django.conf import settings
from utils import parameter_helper
from utils.cities import get_cities as get_city_data
from utils.decorators import check_get_post_request_and_get_params, return_HttpResponse
from utils.plate_model_utils import get_rotation_model
from utils.round_float import round_floats


@check_get_post_request_and_get_params
@return_HttpResponse()
def get_cities(request, params={}):
    """get the coordinates of cities at some paleo-age for a given plate model

    :param time: paleo-age
    :param model: plate model name
    """
    time = parameter_helper.get_float(params, "time", 0.0)
    model = params.get("model", settings.MODEL_DEFAULT).lower()
    city_data = get_city_data()

    print({"names": city_data["names"], "coords": city_data["coords"]})
    if math.isclose(time, 0.0):
        return json.dumps(
            round_floats({"names": city_data["names"], "coords": city_data["coords"]})
        )

    # create features
    features = []
    for name, coords, pid_and_time in zip(
        city_data["names"], city_data["coords"], city_data["pids"][model]
    ):
        f = pygplates.Feature()
        f.set_geometry(pygplates.PointOnSphere(coords[1], coords[0]))
        f.set_name(name)
        f.set_reconstruction_plate_id(pid_and_time[0])
        f.set_valid_time(pid_and_time[1], pid_and_time[2])
        features.append(f)

    # reconstruct
    reconstructed_feature_geometries = []
    pygplates.reconstruct(
        features,
        get_rotation_model(model),
        reconstructed_feature_geometries,
        time,
    )

    paleo_coords = [
        rfg.get_reconstructed_geometry().to_lat_lon_list()[0][::-1]
        for rfg in reconstructed_feature_geometries
    ]

    for rfg in reconstructed_feature_geometries:
        print(rfg.get_reconstructed_geometry().to_lat_lon_list()[0][::-1])

    return json.dumps(
        round_floats({"names": city_data["names"], "coords": paleo_coords})
    )
