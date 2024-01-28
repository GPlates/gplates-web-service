import json
import logging
import math

import pygplates
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from openapi_schema.reconstruct_points_schema import ReconPointsSchema
from rest_framework.decorators import api_view, schema, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from utils.access_control import get_client_ip
from utils.decorators import check_get_post_request_and_get_params, return_HttpResponse
from utils.parameter_helper import (
    get_anchor_plate_id,
    get_bool,
    get_float,
    get_int,
    get_lats_lons,
    get_value_list,
)
from utils.plate_model_utils import (
    UnrecognizedModel,
    get_rotation_model,
    get_static_polygons,
)
from utils.round_float import round_floats

logger = logging.getLogger("default")
access_logger = logging.getLogger("queue")


if settings.THROTTLE:
    throttle_class_list = [AnonRateThrottle]
else:
    throttle_class_list = []


@csrf_exempt
@api_view(["GET", "POST"])
@throttle_classes(throttle_class_list)
@schema(ReconPointsSchema())
@check_get_post_request_and_get_params
@return_HttpResponse()
def reconstruct(request, params={}):
    """http request to reconstruct points

    http://localhost:18000/reconstruct/reconstruct_points/?lats=50,10,50&lons=-100,160,100&time=100&model=PALEOMAP&return_null_points

    :param format: return data format
        1. geojson -- (default) return multipoint geometry. Use [999.99,999.99] for null points to create a valid geojson structure
        2. feature_collection  -- return a geojson feature collection with multiple point features.
        3. simple -- simple return the {"lons":[...], "lats":[...], "pids":[...], "begin_time":[...], "end_time":[...]}
    """

    access_logger.info(get_client_ip(request) + f" {request.get_full_path()}")

    model = params.get("model", settings.MODEL_DEFAULT)
    return_null_points = get_bool(params, "return_null_points", False)
    return_feature_collection = get_bool(params, "fc", False)
    is_reverse = get_bool(params, "reverse", False)
    ignore_valid_time = get_bool(params, "ignore_valid_time", False)
    format = params.get("fmt", "geojson").strip().lower()
    return_simple_data = True if format == "simple" else False
    if format == "feature_collection":
        return_feature_collection = True

    try:
        point_features = []
        p_index = 0
        rotation_model = get_rotation_model(model)
        timef = get_float(params, "time", None)
        anchor_plate_id = get_anchor_plate_id(params)
        lats, lons = get_lats_lons(params)
        assert len(lats) == len(lons)
        pids = get_value_list(params, "pids", int)
        pid = get_int(params, "pid", None)
        if pid is not None and len(pids) > 0:
            raise Exception(
                "The parameter 'pid' and 'pids' are mutually exclusive. Only one of them is allowed. "
            )
        if len(pids) != len(lats):
            pids = len(lats) * [pid]
        times = get_value_list(params, "times", float)

        if timef is not None and len(times) > 0:
            raise Exception(
                "The parameter 'time' and 'times' are mutually exclusive. Only one of them is allowed. "
            )

        if is_reverse and timef is None:
            raise Exception(
                "The parameter 'time' must be present for 'reverse reconstruct'. The 'times' does not make sense for 'reverse reconstruct'. "
            )

        # create point features from input coordinates
        for lat, lon, pid in zip(lats, lons, pids):
            point_feature = pygplates.Feature()
            point_feature.set_geometry(pygplates.PointOnSphere(lat, lon))
            point_feature.set_name(str(p_index))
            if pid:
                point_feature.set_reconstruction_plate_id(pid)
            point_features.append(point_feature)
            p_index += 1
    except pygplates.InvalidLatLonError as e:
        return HttpResponseBadRequest(f"Invalid longitude or latitude ({e}).")
    except UnrecognizedModel as e:
        return HttpResponseBadRequest(
            f"""Unrecognized Rotation Model: {model}.<br> 
        Use <a href="https://gws.gplates.org/info/model_names">https://gws.gplates.org/info/model_names</a> 
        to find all the names of available models."""
        )
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    # assign plate-ids to points using static polygons
    partition_time = timef if is_reverse else 0.0

    #
    # TODO: cache plate id(s)
    #
    # if user has provided plate id(s), do not partition(slow)
    if all(id is None for id in pids):
        properties_to_copy = [pygplates.PartitionProperty.reconstruction_plate_id]
        if not ignore_valid_time:
            properties_to_copy.append(pygplates.PartitionProperty.valid_time_period)

        # LOOK HERE !!!!
        # it seems when the partition_time is not 0
        # the returned assigned_point_features contains reverse reconstructed present-day geometries.
        # so, when doing reverse reconstruct, do not reverse reconstruct again later.
        assigned_point_features = pygplates.partition_into_plates(
            get_static_polygons(model),
            rotation_model,
            point_features,
            properties_to_copy=properties_to_copy,
            reconstruction_time=partition_time,
        )
    else:
        assigned_point_features = point_features

    ret = None
    # reconstruct the points
    if timef is not None:
        # for single time
        if is_reverse:
            lons, lats, pids, btimes, etimes = _reverse_reconstruct(
                assigned_point_features,
                rotation_model,
                timef,
                anchor_plate_id,
                not all(id is None for id in pids),
            )
        else:
            lons, lats, pids, btimes, etimes = _reconstruct(
                assigned_point_features,
                rotation_model,
                timef,
                anchor_plate_id,
            )

        ret = _prepare_return_data(
            lons,
            lats,
            pids,
            btimes,
            etimes,
            return_feature_collection,
            return_simple_data,
            return_null_points,
        )

    elif len(times) > 0:
        # for multiple times
        ret = {}
        for time in times:
            lons, lats, pids, btimes, etimes = _reconstruct(
                assigned_point_features,
                rotation_model,
                time,
                anchor_plate_id,
            )

            # prepare the response to be returned
            ret[str(time)] = _prepare_return_data(
                lons,
                lats,
                pids,
                btimes,
                etimes,
                return_feature_collection,
                return_simple_data,
                return_null_points,
            )

    else:
        return HttpResponseBadRequest(
            f"Either parameter 'time' or 'times' is required. One of the two parameters must present."
        )

    return json.dumps(round_floats(ret))


def _prepare_return_data(
    lons,
    lats,
    pids,
    btimes,
    etimes,
    return_feature_collection,
    return_simple_data,
    return_null_points,
):
    """prepare the return data"""
    if return_feature_collection:
        return _prepare_feature_collection_ret(lons, lats, pids, btimes, etimes)
    elif return_simple_data:
        return _prepare_simle_ret(lons, lats, pids, btimes, etimes)
    else:
        return _prepare_multipoint_ret(lons, lats, return_null_points)


def _prepare_simle_ret(lons, lats, pids, btimes, etimes):
    """prepare the simple data structure to return"""
    _btimes = []
    for t in btimes:
        if t is None:
            _btimes.append(t)
        elif math.isinf(t):
            _btimes.append("distant past")
        else:
            _btimes.append(t)

    _etimes = []
    for t in etimes:
        if t is None:
            _etimes.append(t)
        elif math.isinf(t):
            _etimes.append("distant future")
        else:
            _etimes.append(t)
    return {
        "lons": lons,
        "lats": lats,
        "pids": pids,
        "begin_time": _btimes,
        "end_time": _etimes,
    }


def _reconstruct(
    assigned_point_features,
    rotation_model,
    timef: float,
    anchor_plate_id: int,
):
    """reconstruct"""
    reconstructed_feature_geometries = []
    pygplates.reconstruct(
        assigned_point_features,
        rotation_model,
        reconstructed_feature_geometries,
        timef,
        anchor_plate_id=anchor_plate_id,
    )
    point_count = len(assigned_point_features)
    lons = point_count * [None]
    lats = point_count * [None]
    pids = point_count * [None]
    btimes = point_count * [None]
    etimes = point_count * [None]
    for rfg in reconstructed_feature_geometries:
        lat, lon = rfg.get_reconstructed_geometry().to_lat_lon()
        feature = rfg.get_feature()
        idx = int(feature.get_name())
        lons[idx] = lon
        lats[idx] = lat
    for idx in range(len(assigned_point_features)):
        feature = assigned_point_features[idx]
        pids[idx] = feature.get_reconstruction_plate_id()
        btime, etime = feature.get_valid_time()
        btimes[idx] = btime
        etimes[idx] = etime

    return lons, lats, pids, btimes, etimes


def _reverse_reconstruct(
    assigned_point_features,
    rotation_model,
    timef: float,
    anchor_plate_id: int,
    user_provide_pids_flag: bool,
):
    """reverse reconstruct"""
    # we still need reverse reconstruct if the points had not been partitioned.
    # if user had provided the pids, we did not do partition. So, we need to call pygplates.reverse_reconstruct in that case.
    if user_provide_pids_flag:
        pygplates.reverse_reconstruct(
            assigned_point_features,
            rotation_model,
            timef,
            anchor_plate_id=anchor_plate_id,
        )
    point_count = len(assigned_point_features)
    lons = point_count * [None]
    lats = point_count * [None]
    pids = point_count * [None]
    btimes = point_count * [None]
    etimes = point_count * [None]
    for feature in assigned_point_features:
        lat, lon = feature.get_geometry().to_lat_lon()
        idx = int(feature.get_name())
        lons[idx] = lon
        lats[idx] = lat
        pids[idx] = feature.get_reconstruction_plate_id()
        btime, etime = feature.get_valid_time()
        btimes[idx] = btime
        etimes[idx] = etime
    return lons, lats, pids, btimes, etimes


def _prepare_multipoint_ret(lons, lats, return_null_points):
    """prepare multipoint return data"""

    ret = {"type": "MultiPoint", "coordinates": []}
    for idx in range(len(lons)):
        lon = lons[idx]
        lat = lats[idx]

        if lon is not None and lat is not None:
            ret["coordinates"].append([lon, lat])
        elif return_null_points:
            # return null for invalid coordinates
            ret["coordinates"].append(None)
        else:
            ret["coordinates"].append(
                [999.99, 999.99]
            )  # use 999.99 to indicate invalid coordinates
    return ret


def _prepare_feature_collection_ret(lons, lats, pids, btimes, etimes):
    """prepare feature collection return data"""
    ret = {"type": "FeatureCollection", "features": []}
    for idx in range(len(lons)):
        lon = lons[idx]
        lat = lats[idx]
        begin_time = btimes[idx]
        end_time = etimes[idx]
        pid = pids[idx]

        feat = {"type": "Feature", "geometry": {}}
        if lon is not None and lat is not None:
            feat["geometry"] = {"type": "Point", "coordinates": [lon, lat]}
        else:
            feat["geometry"] = None

        # write out begin and end time
        if begin_time is not None and math.isinf(begin_time):
            begin_time = "distant past"
        if end_time is not None and math.isinf(end_time):
            end_time = "distant future"
        feat["properties"] = {"valid_time": [begin_time, end_time]}

        feat["properties"]["pid"] = pid
        ret["features"].append(feat)
    return ret
