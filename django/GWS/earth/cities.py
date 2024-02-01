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
    http://localhost:18000/earth/get_cities?time=140&model=seton2012

    :param time: paleo-age
    :param model: plate model name

    TODO: get paleo-coordinates of cities for multiple times
    """
    time = parameter_helper.get_float(params, "time", 0.0)
    model = params.get("model", settings.MODEL_DEFAULT).lower()
    city_data = get_city_data()

    if math.isclose(time, 0.0):
        return json.dumps(
            round_floats(
                {
                    "names": city_data["names"],
                    "lons": city_data["lons"],
                    "lats": city_data["lats"],
                }
            )
        )

    # create features
    features = []
    count = 0
    for lon, lat, pid_and_time in zip(
        city_data["lons"],
        city_data["lats"],
        city_data["pids"][model],
    ):
        f = pygplates.Feature()
        f.set_geometry(pygplates.PointOnSphere(lat, lon))
        f.set_name(str(count))
        f.set_reconstruction_plate_id(pid_and_time[0])
        if not isinstance(pid_and_time[1], float):
            begin_time = pygplates.GeoTimeInstant.create_distant_past()
        else:
            begin_time = pid_and_time[1]

        if not isinstance(pid_and_time[2], float):
            end_time = pygplates.GeoTimeInstant.create_distant_future()
        else:
            end_time = pid_and_time[2]
        f.set_valid_time(begin_time, end_time)
        features.append(f)
        count += 1

    # reconstruct
    reconstructed_feature_geometries = []
    pygplates.reconstruct(
        features,
        get_rotation_model(model),
        reconstructed_feature_geometries,
        time,
    )

    paleo_lons = len(city_data["names"]) * [None]
    paleo_lats = len(city_data["names"]) * [None]
    for rfg in reconstructed_feature_geometries:
        lat, lon = rfg.get_reconstructed_geometry().to_lat_lon_list()[0]
        int(rfg.get_feature().get_name())
        paleo_lons[int(rfg.get_feature().get_name())] = lon
        paleo_lats[int(rfg.get_feature().get_name())] = lat

    return json.dumps(
        round_floats(
            {"names": city_data["names"], "lons": paleo_lons, "lats": paleo_lats}
        )
    )


@check_get_post_request_and_get_params
@return_HttpResponse()
def get_present_day_cities(request, params={}):
    """return present day city names, coordinates and pids
    http://localhost:18000/earth/get_present_day_cities
    """
    return json.dumps(get_city_data())
