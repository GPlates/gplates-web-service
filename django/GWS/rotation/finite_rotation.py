import json
import math

import numpy as np
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from lib.quaternions import axis_angle_to_quat, lat_lon_to_cart
from utils.plate_model_utils import get_rotation_model
from utils.round_float import round_floats


@csrf_exempt
def get_plate_ids(request):
    """return all the plate ids in the reconstruction tree at given time
    https://gws.gplates.org/rotation/get_plate_ids?time=100

    :returns: a json list of plate ids
    """
    time = request.GET.get("time", 0)
    model_name = request.GET.get("model", settings.MODEL_DEFAULT)
    try:
        time = float(time)
    except:
        return HttpResponseBadRequest(f"The {time} is invalid. Must be a float number.")

    rotation_model = get_rotation_model(model_name)
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
    """return the finite rotation as pole and angle
    https://gws.gplates.org/rotation/get_euler_pole_and_angle?times=10,50,100&pids=701,801,901
    """
    return get_rotation(request)


#
# return the finite rotation as quaternions.
#
@csrf_exempt
def get_quaternions(request):
    """return finite rotation as quaternions
    https://gws.gplates.org/rotation/get_quaternions?times=10.50.100&pids=701,801,901
    """
    return get_rotation(request, True)


def get_rotation(request, return_quat=False):
    """get finite rotaton as (pole,angle) or quaternions"""
    if request.method == "POST":
        params = request.POST
        if len(list(params.items())) == 0:
            params = json.loads(request.body.decode("utf-8"))
    elif request.method == "GET":
        params = request.GET
    else:
        return HttpResponseBadRequest("ERROR: only accept post and get requests!")

    model_name, times, pids = get_request_parameters(params)

    # return results as {pid_1:[a list of rotation], pid_2:[a list of rotation]}
    # now group the results by "time"
    is_group_by_pid = True if "group_by_pid" in params else False

    rotation_model = get_rotation_model(model_name)

    ret = {}
    ret_by_pids = {}
    for idx, time in enumerate(times):
        r_tree = rotation_model.get_reconstruction_tree(time)
        ret[str(time)] = {}

        # if no pids are given, get all pids from reconstruction tree
        if len(pids) == 0:
            edges = r_tree.get_edges()
            for edge in edges:
                pids.append(edge.get_moving_plate_id())
            pids_ = list(set(pids))
        else:
            pids_ = pids

        for pid in pids_:
            if str(pid) not in ret_by_pids:
                ret_by_pids[str(pid)] = [[0.0, 90.0, 0.0]] * len(times)
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

            if is_group_by_pid:
                ret_by_pids[str(pid)][idx] = ret[str(time)][str(pid)]

    if is_group_by_pid:
        ret = json.dumps(round_floats(ret_by_pids, decimals=8))
    else:
        ret = json.dumps(round_floats(ret, decimals=8))

    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_request_parameters(params):
    """parse parameters from http request"""
    time_str = params.get("times", None)
    pid_str = params.get("pids", None)
    model = params.get("model", settings.MODEL_DEFAULT)
    start_str = params.get("start", None)
    end_str = params.get("end", None)
    step_str = params.get("step", 1)
    try:
        if time_str is not None:
            # make [10.5,20.6,30.5] work
            time_str = "".join(
                c for c in time_str if c.isdecimal() or (c in [".", ","])
            )
            times = [float(t) for t in time_str.split(",")]
        elif all([(start_str is not None), (end_str is not None)]):
            times = np.arange(
                float(start_str), float(end_str), float(step_str)
            ).tolist()
        else:
            times = [0]
        if pid_str and pid_str is not None:
            # make [701,201,301] work
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
