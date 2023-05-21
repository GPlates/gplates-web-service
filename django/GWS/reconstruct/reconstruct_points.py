#
# Copyright and legal info
#
import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, schema, throttle_classes
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.throttling import AnonRateThrottle

from utils.model_utils import (
    get_rotation_model,
    get_static_polygons_filename,
    UnrecognizedModel,
)
from utils.round_float import round_floats
from utils.get_lats_lons import get_lats_lons
from utils.parameter_helper import get_anchor_plate_id, get_pids, get_time


class ReconPointsSchema(AutoSchema):
    """
    OpenAPI schema for reconstruct points method
    """

    def get_components(self, path, method):
        """
        override get_components
        """
        return super().get_components(path, method)

    def get_operation(self, path, method):
        """
        override get_operation
        """
        operation = super().get_operation(path, method)
        parameters = [
            {
                "name": "points",
                "in": "query",
                "description": """list of points long,lat comma separated coordinates of points 
                    to be reconstructed [Required or use "lats" and "lons" parameters]""",
                "schema": {"type": "number"},
            },
            {
                "name": "lats",
                "in": "query",
                "description": """list of latitudes of input points [Required or use "points" parameter]""",
                "schema": {"type": "number"},
            },
            {
                "name": "lons",
                "in": "query",
                "description": """list of latitudes of input points [Required or use "points" parameter]""",
                "schema": {"type": "number"},
            },
            {
                "name": "time",
                "in": "query",
                "description": "time for reconstruction [required]",
                "schema": {"type": "number"},
            },
            {
                "name": "anchor_plate_id",
                "in": "query",
                "description": "integer value for reconstruction anchor plate id [default=0]",
                "schema": {"type": "number"},
            },
            {
                "name": "model",
                "in": "query",
                "description": "name for reconstruction model [defaults to default model from web service settings]",
                "schema": {"type": "string"},
            },
            {
                "name": "pids",
                "in": "query",
                "description": "specify plate id for each point to improve performance",
                "schema": {"type": "string"},
            },
            {
                "name": "pid",
                "in": "query",
                "description": "specify plate id to improve performance. all points use the same plate id",
                "schema": {"type": "number"},
            },
            {
                "name": "return_null_points",
                "in": "query",
                "description": "use null to indicate invalid coordinates. otherwise, use [999.99, 999.99]",
                "schema": {"type": "boolean"},
            },
            {
                "name": "fc",
                "in": "query",
                "description": "flag to return geojson feature collection",
                "schema": {"type": "boolean"},
            },
            {
                "name": "reverse",
                "in": "query",
                "description": "reverse reconstruct paleo-coordinates to present-day coordinates",
                "schema": {"type": "boolean"},
            },
            {
                "name": "ignore_valid_time",
                "in": "query",
                "description": "if this flag presents, the reconstruction will ignore the valid time constraint",
                "schema": {"type": "boolean"},
            },
        ]
        responses = {
            "200": {
                "description": "reconstructed coordinates in json or geojson format",
                "content": {"application/json": {}},
            }
        }
        my_operation = {
            "parameters": parameters,
            "responses": responses,
        }
        if method.lower() == "get":
            my_operation[
                "description"
            ] = """http GET request to reconstruct points.  
                For details and examples, go https://gwsdoc.gplates.org/reconstruction/reconstruct-points"""
            my_operation["summary"] = "GET method to reconstruct points"
        elif method.lower() == "post":
            my_operation[
                "description"
            ] = """http POST request to reconstruct points. 
                Basically the same as 'GET' methon, only allow user to send more points.
                For details and examples, go https://gwsdoc.gplates.org/reconstruction/reconstruct-points"""
            my_operation["summary"] = "POST method to reconstruct points"

        else:
            my_operation = {"summary": "Not implemented yet!"}

        operation.update(my_operation)
        return operation


if settings.THROTTLE:
    throttle_class_list = [AnonRateThrottle]
else:
    throttle_class_list = []


@csrf_exempt
@api_view(["GET", "POST"])
@throttle_classes(throttle_class_list)
@schema(ReconPointsSchema())
def reconstruct(request):
    """http request to reconstruct points"""
    if request.method == "POST":
        params = request.POST
    elif request.method == "GET":
        params = request.GET
    else:
        return HttpResponseBadRequest("Unrecognized request type")

    model = params.get("model", settings.MODEL_DEFAULT)

    return_null_points = True if "return_null_points" in params else False
    return_feature_collection = True if "fc" in params else False
    is_reverse = True if "reverse" in params else False
    ignore_valid_time = True if "ignore_valid_time" in params else False

    try:
        rotation_model = get_rotation_model(model)
        static_polygons_filename = get_static_polygons_filename(model)
    except UnrecognizedModel as e:
        return HttpResponseBadRequest(
            f"""Unrecognized Rotation Model: {model}.<br> 
        Use <a href="https://gws.gplates.org/info/model_names">https://gws.gplates.org/info/model_names</a> 
        to find all available models."""
        )

    # create point features from input coordinates
    p_index = 0
    point_features = []

    try:
        timef = get_time(params)
        anchor_plate_id = get_anchor_plate_id(params)
        lats, lons = get_lats_lons(params)
        pids = get_pids(params, len(lats))

        for lat, lon, pid in zip(lats, lons, pids):
            point_feature = pygplates.Feature()
            point_feature.set_geometry(pygplates.PointOnSphere(lat, lon))
            point_feature.set_name(str(p_index))
            if pid:
                point_feature.set_reconstruction_plate_id(pid)
            point_features.append(point_feature)
            p_index += 1
    except pygplates.InvalidLatLonError as e:
        return HttpResponseBadRequest("Invalid longitude or latitude ({0}).".format(e))
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    # assign plate-ids to points using static polygons
    partition_time = timef if is_reverse else 0.0

    # if user has provided plate id(s), do not partition(slow)
    if all(id is None for id in pids):
        # from time import time
        # start = time()

        properties_to_copy = [pygplates.PartitionProperty.reconstruction_plate_id]
        if not ignore_valid_time:
            properties_to_copy.append(pygplates.PartitionProperty.valid_time_period)

        # LOOK HERE !!!!
        # it seems when the partition_time is not 0
        # the returned assigned_point_features contains reverse reconstructed present-day geometries.
        # so, when doing reverse reconstruct, do not reverse reconstruct again later.
        assigned_point_features = pygplates.partition_into_plates(
            static_polygons_filename,
            rotation_model,
            point_features,
            properties_to_copy=properties_to_copy,
            reconstruction_time=partition_time,
        )

        # end=time()
        # print(f'It took {end - start} seconds!')
    else:
        assigned_point_features = point_features

    # reconstruct the points
    assigned_point_feature_collection = pygplates.FeatureCollection(
        assigned_point_features
    )
    reconstructed_feature_geometries = []
    if not is_reverse:
        pygplates.reconstruct(
            assigned_point_feature_collection,
            rotation_model,
            reconstructed_feature_geometries,
            timef,
            anchor_plate_id=anchor_plate_id,
        )
        print(f"anchor plate id: {anchor_plate_id}")
    else:
        # we still need reverse reconstruct if the points were not partitioned above
        if not all(id is None for id in pids):
            pygplates.reverse_reconstruct(
                assigned_point_feature_collection,
                rotation_model,
                timef,
                anchor_plate_id=anchor_plate_id,
            )

    rfgs = p_index * [None]
    for rfg in reconstructed_feature_geometries:
        rfgs[int(rfg.get_feature().get_name())] = rfg

    assigned_fc = p_index * [None]
    for f in assigned_point_feature_collection:
        assigned_fc[int(f.get_name())] = f

    # prepare the response to be returned
    if not return_feature_collection:
        ret = {"type": "MultiPoint", "coordinates": []}
        for idx in range(p_index):
            lon = None
            lat = None
            if not is_reverse and rfgs[idx]:
                lon = rfgs[idx].get_reconstructed_geometry().to_lat_lon()[1]
                lat = rfgs[idx].get_reconstructed_geometry().to_lat_lon()[0]
            elif is_reverse and assigned_fc[idx]:
                lon = assigned_fc[idx].get_geometry().to_lat_lon()[1]
                lat = assigned_fc[idx].get_geometry().to_lat_lon()[0]

            if lon is not None and lat is not None:
                ret["coordinates"].append([lon, lat])
            elif return_null_points:
                # return null for invalid coordinates
                ret["coordinates"].append(None)
            else:
                ret["coordinates"].append(
                    [999.99, 999.99]
                )  # use 999.99 to indicate invalid coordinates

    else:
        ret = {"type": "FeatureCollection", "features": []}
        for idx in range(p_index):
            lon = None
            lat = None
            begin_time = None
            end_time = None
            pid = 0
            if not is_reverse and rfgs[idx]:
                lon = rfgs[idx].get_reconstructed_geometry().to_lat_lon()[1]
                lat = rfgs[idx].get_reconstructed_geometry().to_lat_lon()[0]
            elif is_reverse and assigned_fc[idx]:
                lon = assigned_fc[idx].get_geometry().to_lat_lon()[1]
                lat = assigned_fc[idx].get_geometry().to_lat_lon()[0]

            if assigned_fc[idx]:
                valid_time = assigned_fc[idx].get_valid_time(None)
                if valid_time:
                    begin_time, end_time = valid_time
                pid = assigned_fc[idx].get_reconstruction_plate_id()

            feat = {"type": "Feature", "geometry": {}}
            if lon is not None and lat is not None:
                feat["geometry"] = {"type": "Point", "coordinates": [lon, lat]}
            else:
                feat["geometry"] = None
            if begin_time is not None and end_time is not None:
                # write out begin and end time
                if begin_time == pygplates.GeoTimeInstant.create_distant_past():
                    begin_time = "distant past"
                if end_time == pygplates.GeoTimeInstant.create_distant_future():
                    end_time = "distant future"
                feat["properties"] = {"valid_time": [begin_time, end_time]}
            else:
                feat["properties"] = {}

            feat["properties"]["pid"] = pid

            ret["features"].append(feat)

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(
        json.dumps(round_floats(ret)), content_type="application/json"
    )

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
