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
    get_rotation_model,
    get_static_polygons,
)
from utils.round_float import round_floats

logger = logging.getLogger("default")
access_logger = logging.getLogger("queue")
cache = caches[settings.CACHE_NAME]

SHIELDS = ["Arabia"]


def read_labels(filepath: str) -> list:
    """return a list of label dictionaries
    [{"label": label, "lat": lat, "lon": lon, "fromtime": from_time, "totime": to_time,}, {...}, ...]

    :param filepath: the path to the file which contains the label data, for example f"{settings.EARTH_STORE_DIR}/labels/labels-continents.txt", labels-oceans.txt, labels-cratons.txt

    :return: a list of label dictionaries
    """

    labels = []
    with open(
        filepath,
        "rt",
        encoding="utf-8",
    ) as csv_fp:
        for line in csv_fp:
            items = line.split("|")
            # print(items)
            if len(items) < 5:  # ignore when length is wrong
                print(f"ignore invlid line: {line}")
                continue
            try:
                label = items[1].strip()
                lat = float(items[3])
                lon = float(items[2])
                from_time = int(items[4])
                to_time = int(items[5])
                # comments = items[6].strip()
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
                    # "comments": comments,
                }
            )

    return labels


def get_label_pids(model: str, label_data: list) -> list[int]:
    """return the plate IDs of the labels for a given model.

    :param model: the given model name
    :param label_data: the list of labels. [{"label": label, "lat": lat, "lon": lon, "fromtime": from_time, "totime": to_time,},{...},...]

    :return: a list of plate IDs for the labels
    """
    point_features = []
    for label in label_data:
        point_feature = pygplates.Feature()
        point_feature.set_geometry(pygplates.PointOnSphere(label["lat"], label["lon"]))
        point_features.append(point_feature)

    # assign plate-ids to points using static polygons
    assigned_point_features = pygplates.partition_into_plates(
        get_static_polygons(model),
        get_rotation_model(model),
        point_features,
        properties_to_copy=[pygplates.PartitionProperty.reconstruction_plate_id],
        reconstruction_time=0.0,
    )

    assert len(point_features) == len(assigned_point_features)

    return [f.get_reconstruction_plate_id() for f in assigned_point_features]


def reconstruct_labels(label_data: list, model: str, time: float, pids: list):
    """reconstruct the label coordinates. return a list of names and reconstructed coordinates
    the length of input lable list may be different from the output list because some labels may not exist at the time

    :param label_data: the list of labels. [{"label": label, "lat": lat, "lon": lon, "fromtime": from_time, "totime": to_time,},{...},...]
    :param model: the name of reconstruction model
    :param time: the reconstruction time
    :param pids: the labels' plate IDs

    :return: a tuple of lists (label_name, lons, lats)
    """
    names = []
    lats = []
    lons = []
    plate_ids = []
    for row in zip(label_data, pids):
        if row[0]["fromtime"] >= time and row[0]["totime"] <= time:
            names.append(row[0]["label"])
            lons.append(row[0]["lon"])
            lats.append(row[0]["lat"])
            plate_ids.append(row[1])

    if time != 0:
        point_features = []
        for lat, lon, name, pid in zip(lats, lons, names, plate_ids):
            point_feature = pygplates.Feature()
            point_feature.set_geometry(pygplates.PointOnSphere(lat, lon))
            point_feature.set_name(name)
            if pid:
                point_feature.set_reconstruction_plate_id(int(pid))
            point_features.append(point_feature)

        rotation_model = get_rotation_model(model)

        # reconstruct the points
        reconstructed_feature_geometries = []
        pygplates.reconstruct(
            point_features,
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

    else:
        return names, lons, lats


def get_labels(request):
    """get_labels request handler
    http://localhost:18000/earth/get_labels?time=300&model=merdith2021
    """
    if request.method != "GET":
        return HttpResponseBadRequest("Only GET request is supported!")

    access_logger.info(get_client_ip(request) + f" {request.get_full_path()}")

    time = parameter_helper.get_float(request.GET, "time", 0.0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    # try to get the label data from cache
    # if the label data is not found in the cache, load the data from files
    continent_label_data = cache.get("earth-continent-labels")
    if not continent_label_data:
        continent_label_data = read_labels(
            f"{settings.EARTH_STORE_DIR}/labels/labels-continents.txt"
        )
        cache.set("earth-continent-labels", continent_label_data)
    ocean_label_data = cache.get("earth-ocean-labels")

    if not ocean_label_data:
        ocean_label_data = read_labels(
            f"{settings.EARTH_STORE_DIR}/labels/labels-oceans.txt"
        )
        cache.set("earth-ocean-labels", ocean_label_data)
    craton_label_data = cache.get("earth-craton-labels")

    if not craton_label_data:
        craton_label_data = read_labels(
            f"{settings.EARTH_STORE_DIR}/labels/labels-cratons.txt"
        )
        cache.set("earth-craton-labels", craton_label_data)

    # try to get the labels' plate ID from cache first
    # if not found in cache, use pygplates to assign plate IDs
    craton_pids = cache.get(f"earth-craton-pids-{model}")
    if craton_pids is None:
        craton_pids = get_label_pids(model, craton_label_data)
        cache.set(f"earth-craton-pids-{model}", craton_pids)

    continent_pids = cache.get(f"earth-continent-pids-{model}")
    if continent_pids is None:
        continent_pids = get_label_pids(model, continent_label_data)
        cache.set(f"earth-continent-pids-{model}", continent_pids)

    # prepare ocean labels
    oceans_ret = []
    for row in ocean_label_data:
        if row["fromtime"] >= time and row["totime"] <= time:
            oceans_ret.append((row["label"], row["lat"], row["lon"], "ocean"))

    try:
        # prepare continent labels
        rnames, rlons, rlats = reconstruct_labels(
            continent_label_data, model, time, pids=continent_pids
        )
        continents_ret = list(zip(rnames, rlats, rlons, ["continent"] * len(rnames)))

        # prepare craton labels
        rnames, rlons, rlats = reconstruct_labels(
            craton_label_data, model, time, pids=craton_pids
        )
        # find the label is a shield or craton
        craton_or_shield = []
        for n in rnames:
            if n in SHIELDS:
                craton_or_shield.append("shield")
            else:
                craton_or_shield.append("craton")
        cratons_ret = list(zip(rnames, rlats, rlons, craton_or_shield))

    except pygplates.InvalidLatLonError as e:
        return HttpResponseBadRequest(f"Invalid longitude or latitude ({e}).")
    except UnrecognizedModel as e:
        return HttpResponseBadRequest(
            f"""Unrecognized Rotation Model: {model}.<br> 
            Use <a href="https://gws.gplates.org/info/model_names">https://gws.gplates.org/info/model_names</a> 
            to find all available models."""
        )

    response = HttpResponse(
        json.dumps(round_floats(oceans_ret + continents_ret + cratons_ret)),
        content_type="application/json",
    )

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
