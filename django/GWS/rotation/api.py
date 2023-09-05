import _rotation as rotation
import json
import math

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from utils.model_utils import get_rotation_files


def rotate(request):
    """
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
    return a map
    http://localhost:18000/rotation/get_rotation_map/?model=MERDITH2021
    """
    model_name = request.GET.get("model", settings.MODEL_DEFAULT)

    rotation_data = []
    for rot_file in get_rotation_files(model_name):
        with open(
            f"{settings.MODEL_STORE_DIR}/{model_name}/{rot_file}", "r", encoding="utf-8"
        ) as fp:
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
