#
# put your copyright, software license and legal information here.
#
import json
import math

import pygplates
from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
)
from django.views.decorators.csrf import csrf_exempt
from utils.model_utils import get_reconstruction_model_dict
from utils.round_float import round_floats

#
# return all the plate ids in the reconstruction tree at given time
#
@csrf_exempt
def get_plate_ids(request):
    time = request.GET.get("time", 0)
    model_name = request.GET.get("model", settings.MODEL_DEFAULT)
    try:
        time = float(time)
    except:
        return HttpResponseBadRequest(f"The {time} is invalid. Must be a float number.")

    model_dict = get_reconstruction_model_dict(model_name)
    if not model_dict:
        return HttpResponseBadRequest(
            f'The "model" ({model_name}) cannot be recognized.'
        )

    rotation_model = pygplates.RotationModel(
        [
            f"{settings.MODEL_STORE_DIR}/{model_name}/{rot_file}"
            for rot_file in model_dict["RotationFile"]
        ]
    )
    edges = rotation_model.get_reconstruction_tree(time).get_edges()
    pids = []
    for edge in edges:
        pids.append(edge.get_fixed_plate_id())
        pids.append(edge.get_moving_plate_id())
    pids = list(set(pids))
    pids.sort()
    ret = json.dumps(round_floats(pids))
    return HttpResponse(ret, content_type="application/json")


#
# return the finite rotation as a tuple of pole longitude, pole latitude and angle (all in degrees).
#
@csrf_exempt
def get_euler_pole_and_angle(request):
    return get_rotation(request)


#
# return the finite rotation as quaternions.
#
@csrf_exempt
def get_quaternions(request):
    return get_rotation(request, True)


#
# return the finite rotation
# https://gws.gplates.org/rotation/get_euler_pole_and_angle?times=10,50,100&pids=701,801,901
#
def get_rotation(request, return_quat=False):
    if request.method == "POST":
        params = request.POST
    elif request.method == "GET":
        params = request.GET
    else:
        return HttpResponseBadRequest("ERROR: only accept post and get requests!")

    model_name, times, pids = get_request_parameters(params)

    model_dict = get_reconstruction_model_dict(model_name)
    if not model_dict:
        return HttpResponseBadRequest(
            f'The "model" ({model_name}) cannot be recognized.'
        )

    rotation_model = pygplates.RotationModel(
        [
            f"{settings.MODEL_STORE_DIR}/{model_name}/{rot_file}"
            for rot_file in model_dict["RotationFile"]
        ]
    )

    ret = {}
    for time in times:
        r_tree = rotation_model.get_reconstruction_tree(time)
        ret[str(time)] = {}

        # if not pids are given, get all pids from reconstruction tree
        if len(pids) == 0:
            edges = r_tree.get_edges()
            for edge in edges:
                pids.append(edge.get_fixed_plate_id())
                pids.append(edge.get_moving_plate_id())
            pids_ = list(set(pids))
        else:
            pids_ = pids

        for pid in pids_:
            finite_rotation = r_tree.get_equivalent_total_rotation(pid)
            (
                pole_lat,
                pole_lon,
                angle,
            ) = finite_rotation.get_lat_lon_euler_pole_and_angle_degrees()

            if return_quat:
                axis = lat_lon_to_cart(math.radians(pole_lat), math.radians(pole_lon))
                ret[str(time)][str(pid)] = axis_angle_to_quat(axis, math.radians(angle))
            else:
                ret[str(time)][str(pid)] = [pole_lon, pole_lat, angle]

    ret = json.dumps(round_floats(ret))

    return HttpResponse(ret, content_type="application/json")


#
# parse parameters from http request
#
def get_request_parameters(params):
    time_str = params.get("times", "0")
    pid_str = params.get("pids", None)
    model = params.get("model", settings.MODEL_DEFAULT)
    try:
        # make [10.5,20.6,30.5] or [701,201,301] work
        time_str = "".join(c for c in time_str if c.isdecimal() or (c in [".", ","]))
        times = [float(t) for t in time_str.split(",")]
        if pid_str and pid_str is not None:
            pid_str = "".join(c for c in pid_str if c.isdecimal() or c == ",")
            pids = [int(p) for p in pid_str.split(",")]
        else:
            pids = []  # pid_str is None or empty
    except:
        raise InvalidParameters()
    return model, list(set(times)), list(set(pids))  # return unique times and pids


# Raised when failed to parse parameters
class InvalidParameters(Exception):
    pass


def normalize(v, tolerance=0.00001):
    mag2 = sum(n * n for n in v)
    if abs(mag2 - 1.0) > tolerance:
        mag = math.sqrt(mag2)
        v = tuple(n / mag for n in v)
    return v


def axis_angle_to_quat(v, theta):
    v = normalize(v)
    x, y, z = v
    theta /= 2
    w = math.cos(theta)
    x = x * math.sin(theta)
    y = y * math.sin(theta)
    z = z * math.sin(theta)
    return w, x, y, z


def lat_lon_to_cart(lat, lon):
    x = math.cos(lat) * math.cos(lon)
    y = math.cos(lat) * math.sin(lon)
    z = math.sin(lat)
    return x, y, z
