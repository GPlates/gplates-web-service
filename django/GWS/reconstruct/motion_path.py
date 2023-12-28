import json

import numpy as np
import pygplates
from django.conf import settings
from django.http import HttpResponse
from utils.plate_model_utils import get_rotation_model
from utils.round_float import round_floats


def get_motion_path(request):
    """
    http GET request to retrieve reconstructed static polygons

    **usage**

    <http-address-to-gws>/reconstruct/motion_path/seedpoints=\ *points*\&timespec=\ *time_list*\&fixplate=\ *fixed_plate_id*\&movplate=\ *moving_plate_id*\&time=\ *reconstruction_time*\&model=\ *reconstruction_model*

    :param seedpoints: integer value for reconstruction anchor plate id [required]

    :param timespec: specification for times for motion path construction, in format 'mintime,maxtime,increment' [defaults to '0,100,10']

    :param time: time for reconstruction [default=0]

    :param fixplate: integer plate id for fixed plate [default=0]

    :param movplate: integer plate id for moving plate [required]

    :param model: name for reconstruction model [defaults to default model from web service settings]

    :returns:  json containing reconstructed motion path features
    """
    seedpoints = request.GET.get("seedpoints", None)
    times = request.GET.get("timespec", "0,100,10")
    reconstruction_time = request.GET.get("time", 0)
    RelativePlate = request.GET.get("fixplate", 0)
    MovingPlate = request.GET.get("movplate", 701)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    points = []
    if seedpoints:
        ps = seedpoints.split(",")
        if len(ps) % 2 == 0:
            for lat, lon in zip(ps[1::2], ps[0::2]):
                points.append((float(lat), float(lon)))

    seed_points_at_digitisation_time = pygplates.MultiPointOnSphere(points)

    if times:
        ts = times.split(",")
        if len(ts) == 3:
            times = np.arange(float(ts[0]), float(ts[1]) + 0.1, float(ts[2]))

    rotation_model = get_rotation_model(model)

    # Create the motion path feature
    # seed_points_at_digitisation_time = pygplates.MultiPointOnSphere([SeedPoint])
    motion_path_feature = pygplates.Feature.create_motion_path(
        seed_points_at_digitisation_time,
        times=times,
        valid_time=(2000, 0),
        relative_plate=int(RelativePlate),
        reconstruction_plate_id=int(MovingPlate),
    )

    # Create the shape of the motion path
    # reconstruction_time = 0
    reconstructed_motion_paths = []
    pygplates.reconstruct(
        motion_path_feature,
        rotation_model,
        reconstructed_motion_paths,
        float(reconstruction_time),
        reconstruct_type=pygplates.ReconstructType.motion_path,
    )

    data = {"type": "FeatureCollection"}
    data["features"] = []
    for reconstructed_motion_path in reconstructed_motion_paths:
        Dist = []
        for segment in reconstructed_motion_path.get_motion_path().get_segments():
            Dist.append(segment.get_arc_length() * pygplates.Earth.mean_radius_in_kms)
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        feature["geometry"]["type"] = "LineString"
        #### NOTE CODE TO FLIP COORDINATES TO
        feature["geometry"]["coordinates"] = [
            (lon, lat)
            for lat, lon in reconstructed_motion_path.get_motion_path().to_lat_lon_list()
        ]
        feature["geometry"]["distance"] = Dist
        feature["properties"] = {}
        data["features"].append(feature)

    ret = json.dumps(round_floats(data))

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
