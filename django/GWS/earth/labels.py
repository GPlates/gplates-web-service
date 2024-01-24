import json
import logging

import pygplates
from django.conf import settings
from django.core.cache import caches
from django.http import HttpResponse, HttpResponseBadRequest
from utils import parameter_helper
from utils.access_control import get_client_ip
from utils.plate_model_utils import (
    UnrecognizedModel,
    get_model_name_list,
    get_rotation_model,
    get_static_polygons,
)
from utils.round_float import round_floats

logger = logging.getLogger("default")
access_logger = logging.getLogger("queue")
cache = caches[settings.get_cache_name()]


def read_labels():
    """return a list of labels

    [
        {
            "label": label,
            "lat": lat,
            "lon": lon,
            "fromtime": from_time,
            "totime": to_time,
        }
    ]

    """
    d = cache.get("earth-labels")
    if d is not None:
        return d

    labels = []
    with open(f"{settings.EARTH_STORE_DIR}/labels/labels.csv", "rt") as csv_fp:
        for line in csv_fp:
            items = line.split(",")
            if len(items) < 5:  # ignore when length is wrong
                print(f"ignore invlid line: {line}")
                continue
            try:
                label = items[0]
                lat = float(items[1])
                lon = float(items[2])
                from_time = int(items[3])
                to_time = int(items[4])
            except:
                print(f"ignore invlid line: {line}")
                continue

            labels.append(
                {
                    "label": label,
                    "lat": lat,
                    "lon": lon,
                    "fromtime": from_time,
                    "totime": to_time,
                }
            )
    cache.set("earth-labels", labels)
    return labels


read_labels()


def read_label_pids(model):
    """return the pids of labels' coordinates

    :param model: model name
    """
    return get_label_pids()[model.lower()]


def get_label_pids():
    """return a dictionary of pids, such as
    {
        "seton":[123,234,566],
        'muller2019': [321,434,546]
    }
    """
    d = cache.get("earth-labels-pids")
    if d is not None:
        return d

    point_features = []
    for label in read_labels():
        point_feature = pygplates.Feature()
        point_feature.set_geometry(pygplates.PointOnSphere(label["lat"], label["lon"]))
        point_features.append(point_feature)

    pid_dict = {}
    for model in get_model_name_list(settings.MODEL_REPO_DIR):
        # assign plate-ids to points using static polygons
        assigned_point_features = pygplates.partition_into_plates(
            get_static_polygons(model),
            get_rotation_model(model),
            point_features,
            properties_to_copy=[
                pygplates.PartitionProperty.reconstruction_plate_id,
                pygplates.PartitionProperty.valid_time_period,
            ],
            reconstruction_time=0.0,
        )

        assert len(point_features) == len(assigned_point_features)

        pids = [f.get_reconstruction_plate_id() for f in assigned_point_features]
        pid_dict[model] = pids
        cache.set("earth-labels-pids", pid_dict)
    return pid_dict


get_label_pids()


def reconstruct_labels(names, lons, lats, model, time, pids=[]):
    """reconstruct the label coordinates. return a list of names and reconstructed coordinates
    the length of input lable list may be different from the output list because some labels may not exist at the time
    """
    assert len(lats) == len(lons)
    assert len(names) == len(lons)
    point_features = []
    if not pids:
        tpids = [None] * len(names)
    else:
        tpids = pids

    for lat, lon, name, pid in zip(lats, lons, names, tpids):
        point_feature = pygplates.Feature()
        point_feature.set_geometry(pygplates.PointOnSphere(lat, lon))
        point_feature.set_name(name)
        if pid:
            point_feature.set_reconstruction_plate_id(int(pid))
        point_features.append(point_feature)

    try:
        rotation_model = get_rotation_model(model)
    except UnrecognizedModel as e:
        return HttpResponseBadRequest(
            f"""Unrecognized Rotation Model: {model}.<br> 
        Use <a href="https://gws.gplates.org/info/model_names">https://gws.gplates.org/info/model_names</a> 
        to find all available models."""
        )

    if not pids:
        assigned_point_features = pygplates.partition_into_plates(
            get_static_polygons(model),
            rotation_model,
            point_features,
            properties_to_copy=[
                pygplates.PartitionProperty.reconstruction_plate_id,
                pygplates.PartitionProperty.valid_time_period,
            ],
            reconstruction_time=time,
        )
    else:
        assigned_point_features = point_features

    # reconstruct the points
    assigned_point_feature_collection = pygplates.FeatureCollection(
        assigned_point_features
    )
    reconstructed_feature_geometries = []

    pygplates.reconstruct(
        assigned_point_feature_collection,
        rotation_model,
        reconstructed_feature_geometries,
        time,
    )

    rnames = []
    rlons = []
    rlats = []
    for rfg in reconstructed_feature_geometries:
        rnames.append(rfg.get_feature().get_name())
        r_lat_lon = rfg.get_reconstructed_geometry().to_lat_lon()
        rlons.append(r_lat_lon[1])
        rlats.append(r_lat_lon[0])
    return rnames, rlons, rlats


def get_labels(request):
    """http://localhost:18000/earth/get_labels?time=300&model=merdith2021"""
    if request.method != "GET":
        return HttpResponseBadRequest("Only GET request is supported!")

    access_logger.info(get_client_ip(request) + f" {request.get_full_path()}")

    time = parameter_helper.get_float(request.GET, "time", 0.0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    labels = read_labels()
    try:
        pids = read_label_pids(model)
    except FileNotFoundError as e:
        pids = []

    if len(pids) != len(labels):
        logger.warning(
            f"The number of PIDs({len(pids)}) is not the same with the number of labels({len(labels)}. And this will slow down the response.)"
        )
        pids = [None] * len(labels)
    names = []
    lons = []
    lats = []
    oceans = []
    for row in labels:
        if row["fromtime"] >= time and row["totime"] <= time:
            label = " ".join(row["label"].split(" "))
            if label.endswith("Ocean"):
                oceans.append((label, row["lat"], row["lon"]))
            else:
                names.append(label)
                lons.append(row["lon"])
                lats.append(row["lat"])

    if time != 0:
        try:
            rnames, rlons, rlats = reconstruct_labels(
                names, lons, lats, model, time, pids=pids
            )
        except pygplates.InvalidLatLonError as e:
            return HttpResponseBadRequest(f"Invalid longitude or latitude ({e}).")
    else:
        rnames = names
        rlats = lats
        rlons = lons

    response = HttpResponse(
        json.dumps(round_floats(oceans + list(zip(rnames, rlats, rlons)))),
        content_type="application/json",
    )

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
