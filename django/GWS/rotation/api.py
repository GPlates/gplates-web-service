import json
import math

import lib.rotation as rotation
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from utils.plate_model_utils import get_rotation_files, get_rotation_model


def rotate(request):
    """rotate a point by axis and angle
    http://localhost:18000/rotation/rotate/?point=120,45&axis=20,-45&angle=20
    """
    point_str = request.GET.get("point", None)
    axis_str = request.GET.get("axis", None)
    angle_str = request.GET.get("angle", None)
    if not point_str or not axis_str:
        return HttpResponseBadRequest(
            "One point, one axis and angle are required in the request!"
        )
    try:
        point = point_str.split(",")
        axis = axis_str.split(",")

        lon_point = float(point[0])
        lat_point = float(point[1])
        lon_axis = float(axis[0])
        lat_axis = float(axis[1])

        angle = float(angle_str)
    except:
        return HttpResponseBadRequest("Invalid points, axis or angle!")

    new_point = rotation.rotate(
        (math.radians(lat_point), math.radians(lon_point)),
        (math.radians(lat_axis), math.radians(lon_axis)),
        angle,
    )

    ret = {"point": (math.degrees(new_point[1]), math.degrees(new_point[0]))}

    response = HttpResponse(json.dumps(ret), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_rotation_map(request):
    """
    return a map of the rotation model
    http://localhost:18000/rotation/get_rotation_map/?model=MERDITH2021
    for example:
    {
        "101": [
            {"fpid": 111, "times": [0.0, 10.], "plats": [90.0, 81.0], "plons": [0.0, 22.9], "angles": [0.0, 2.84]}
            {"fpid": 222, "times": [10.0, 20.], "plats": [90.0, 81.0], "plons": [0.0, 22.9], "angles": [0.0, 2.84]}
        ],
         "102": [
            {"fpid": 333, "times": [0.0, 100], "plats": [90.0, 81.0], "plons": [0.0, 22.9], "angles": [0.0, 2.84]}
            {"fpid": 444, "times": [100, 200], "plats": [90.0, 81.0], "plons": [0.0, 22.9], "angles": [0.0, 2.84]}
        ],
        ....
        ....
    }
    """
    model_name = request.GET.get("model", settings.MODEL_DEFAULT)

    rotation_data = []
    for rot_file in get_rotation_files(model_name):
        with open(rot_file, "r", encoding="utf-8") as fp:
            for line in fp:
                items = line.split()
                # print(items)
                try:
                    if len(items) < 6:
                        raise Exception(f"Invalid rotation line {line} ")
                    plate_id = int(items[0])
                    time = float(items[1])
                    pole_lat = float(items[2])
                    pole_lon = float(items[3])
                    angle = float(items[4])
                    fixed_plate_id = int(items[5])
                    rotation_data.append(
                        [plate_id, time, pole_lat, pole_lon, angle, fixed_plate_id]
                    )
                except:
                    print(f"Invalid rotation line {line} ")
                    continue

    rotation_data.sort(key=lambda x: x[0])  # sort by plate id first
    # create a map using the plate id as key
    data_map = {}
    for row in rotation_data:
        plate_id_str = str(row[0])
        if plate_id_str in data_map:
            data_map[plate_id_str].append(row[1:])
        else:
            data_map[plate_id_str] = [row[1:]]

    for pid in data_map:
        data_map[pid].sort(key=lambda x: x[0])  # sort by time now
        fixed_pid = -1
        time_buf = []
        lat_buf = []
        lon_buf = []
        angle_buf = []
        row_buf = []
        ignore_next_line = False
        for idx, row in enumerate(data_map[pid]):
            if ignore_next_line:
                ignore_next_line = False
                continue
            if fixed_pid != row[4]:
                if fixed_pid == -1:  # process the first rows
                    fixed_pid = row[4]
                    time_buf.append(row[0])
                    lat_buf.append(row[1])
                    lon_buf.append(row[2])
                    angle_buf.append(row[3])
                else:
                    if idx + 1 < len(data_map[pid]):
                        # crossover problem
                        # this only happens in the situation below
                        # time fixed-plate-id
                        # 50 701
                        # 60 701
                        # 70 801 <-------
                        # 70 701 <-------
                        # 80 801
                        # 90 801
                        if (
                            math.isclose(row[0], data_map[pid][idx + 1][0])
                            and data_map[pid][idx + 1][4] == fixed_pid
                        ):
                            time_buf.append(data_map[pid][idx + 1][0])
                            lat_buf.append(data_map[pid][idx + 1][1])
                            lon_buf.append(data_map[pid][idx + 1][2])
                            angle_buf.append(data_map[pid][idx + 1][3])
                            ignore_next_line = True
                    row_buf.append(
                        {
                            "fpid": fixed_pid,
                            "times": time_buf,
                            "plats": lat_buf,
                            "plons": lon_buf,
                            "angles": angle_buf,
                        }
                    )
                    fixed_pid = row[4]
                    time_buf = [row[0]]
                    lat_buf = [row[1]]
                    lon_buf = [row[2]]
                    angle_buf = [row[3]]
            else:
                # when the fixed plate id does not change
                time_buf.append(row[0])
                lat_buf.append(row[1])
                lon_buf.append(row[2])
                angle_buf.append(row[3])
        row_buf.append(
            {
                "fpid": fixed_pid,
                "times": time_buf,
                "plats": lat_buf,
                "plons": lon_buf,
                "angles": angle_buf,
            }
        )
        data_map[pid] = row_buf

    ret = data_map

    response = HttpResponse(json.dumps(ret), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_edges_of_pid(edges, pid):
    """get edges which have the given fixed plate id

    :param edges: all edges in the reconstruction tree
    :param pid: fixed plate id
    :returns: the edges whose fixed plate id is the same with the given one
    """
    return [e for e in edges if e[0] == pid]


def get_reconstruction_tree_edges(request):
    """return edges in a reconstruction tree at given time
    http://localhost:18000/rotation/get_reconstruction_tree_edges/?model=MERDITH2021&time=100&level=4&pids=452,447,712

    :param level: the numbre of tree levels to return. if 0 or not present, means all

    :returns: a list of [fixed plate ID, moving plate ID]
    """

    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    level = request.GET.get("level", 3)
    pids_str = request.GET.get("pids", "")
    pids = []
    try:
        time = float(time)
        level = int(level)
        if len(pids_str) > 0:
            for p in pids_str.split(","):
                pids.append(int(p))
    except:
        return HttpResponseBadRequest(f"time: {time}, level: {level}, pids:{pids_str}")

    rotation_model = get_rotation_model(model)
    tree = rotation_model.get_reconstruction_tree(time)
    edges = tree.get_edges()

    edge_list = list(
        set([(e.get_fixed_plate_id(), e.get_moving_plate_id()) for e in edges])
    )

    if level > 0 or len(pids) > 0:
        edges_buf = []

        fp = set([e[0] for e in edge_list])
        mp = set([e[1] for e in edge_list])
        if len(pids) == 0:
            pids = [i for i in fp if i not in mp]  # get the roots
        safe_guard = 0
        while True:
            new_pids = []
            for pid in pids:
                es = get_edges_of_pid(edge_list, pid)
                edges_buf.extend(es)
                new_pids.extend([i[1] for i in es])
            pids = set(new_pids)
            if level > 0:
                level -= 1
                if level == 0:
                    break
            elif len(new_pids) == 0:
                break
            safe_guard += 1
            if safe_guard > 20:
                break
        edge_list = edges_buf

    response = HttpResponse(json.dumps(edge_list), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_reconstruction_tree_height(request):
    """return the height of the reconstruction tree
    http://localhost:18000/rotation/get_reconstruction_tree_height?pid=304

    """
    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    pid = request.GET.get("pid", 0)

    try:
        pid = int(pid)
    except:
        return HttpResponseBadRequest(f"The parameter 'pid' is required!")

    rotation_model = get_rotation_model(model)
    tree = rotation_model.get_reconstruction_tree(time)

    height = 1

    def traverse_sub_tree(edge, depth):
        nonlocal height
        if depth > height:
            height = depth

        for child_edge in edge.get_child_edges():
            traverse_sub_tree(child_edge, depth=depth + 1)

    if pid:
        traverse_sub_tree(tree.get_edge(pid), depth=1)
    else:
        for anchor_plate_edge in tree.get_anchor_plate_edges():
            # print(
            #    f">>>>{anchor_plate_edge.get_fixed_plate_id()}>>>{anchor_plate_edge.get_moving_plate_id()}"
            # )
            traverse_sub_tree(anchor_plate_edge, depth=2)

    response = HttpResponse(json.dumps(height), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_reconstruction_tree_leaves(request):
    """return all the leaves of the reconstruction tree
    http://localhost:18000/rotation/get_reconstruction_tree_leaves
    """
    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    rotation_model = get_rotation_model(model)
    tree = rotation_model.get_reconstruction_tree(time)

    leaves = []

    def traverse_sub_tree(edge):
        nonlocal leaves
        child_edges = edge.get_child_edges()
        if len(child_edges) == 0:
            leaves.append(edge.get_moving_plate_id())
        else:
            for child_edge in edge.get_child_edges():
                traverse_sub_tree(child_edge)

    for anchor_plate_edge in tree.get_anchor_plate_edges():
        traverse_sub_tree(anchor_plate_edge)

    response = HttpResponse(
        json.dumps(list(set(leaves))), content_type="application/json"
    )

    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_ancestors_in_reconstruction_tree(request):
    """return all ancestors PIDs
    http://localhost:18000/rotation/get_ancestors_in_reconstruction_tree?pid=101
    """
    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    pid = request.GET.get("pid", None)

    try:
        pid = int(pid)
    except:
        return HttpResponseBadRequest(f"The parameter 'pid' is required!")

    rotation_model = get_rotation_model(model)
    tree = rotation_model.get_reconstruction_tree(time)
    edge = tree.get_edge(pid)
    ancestors = []
    while edge:
        ancestors.append(edge.get_fixed_plate_id())
        edge = edge.get_parent_edge()

    response = HttpResponse(json.dumps(ancestors), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response
