import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, schema, throttle_classes
from rest_framework.throttling import AnonRateThrottle

from utils.docstr_schema import DocstrSchema
from utils.model_utils import get_rotation_model, get_static_polygons_filename
from utils.round_float import round_floats

"""
http GET request to reconstruct points

**usage**

<http-address-to-gws>/reconstruct/reconstruct_points/points=\ *points*\&plate_id=\ *anchor_plate_id*\&time=\ *reconstruction_time*\&model=\ *reconstruction_model*

**parameters:**

*points* : list of points long,lat comma separated coordinates of points to be reconstructed [Required]

*anchor_plate_id* : integer value for reconstruction anchor plate id [default=0]

*time* : time for reconstruction [required]

*model* : name for reconstruction model [defaults to default model from web service settings]

**returns:**

json list of long,lat reconstructed coordinates
"""


@csrf_exempt
@api_view(["GET", "POST"])
@throttle_classes([AnonRateThrottle])
@schema(DocstrSchema())
def reconstruct(request):
    """
    get:
      description: http GET request to reconstruct points
      summary: reconstruct points
      parameters:
        - name: points
          in: query
          description: the coordinates of points
          schema:
            type: number
        - name: time
          in: query
          description: paleo-time
          schema:
            type: number

      responses:
        '200':
          description: return reconstructed coordinates
          content:
            'application/json': {}
    post:
      description: basically the same as "get". allow user to send more points
      summary: reconstruct points
      parameters:
        - name: points
          in: query
          description: the coordinates of points
          schema:
            type: number
        - name: time
          in: query
          description: paleo-time
          schema:
            type: number
      responses:
        '200':
          description: return reconstructed coordinates
          content:
            'application/json': {}
    """
    if request.method == "POST":
        params = request.POST
    elif request.method == "GET":
        params = request.GET
    else:
        return HttpResponseBadRequest("Unrecognized request type")

    points = params.get("points", None)
    anchor_plate_id = params.get("pid", 0)
    time = params.get("time", None)
    model = params.get("model", settings.MODEL_DEFAULT)
    pids_str = params.get("pids", None)
    # print(pids_str)
    pid_str = params.get("pid", None)

    return_null_points = True if "return_null_points" in params else False
    return_feature_collection = True if "fc" in params else False
    is_reverse = True if "reverse" in params else False

    timef = 0.0
    if not time:
        return HttpResponseBadRequest('The "time" parameter cannot be empty.')
    else:
        try:
            timef = float(time)
        except:
            return HttpResponseBadRequest(
                'The "time" parameter is invalid ({0}).'.format(time)
            )

    try:
        anchor_plate_id = int(anchor_plate_id)
    except:
        return HttpResponseBadRequest(
            'The "anchor_plate_id" parameter is invalid ({0}).'.format(anchor_plate_id)
        )

    rotation_model = get_rotation_model(model)
    static_polygons_filename = get_static_polygons_filename(model)

    # create point features from input coordinates
    p_index = 0
    point_features = []
    if points:
        ps = points.split(",")
        ps_len = len(ps)
        if ps_len % 2 == 0:
            try:
                if pids_str:
                    pids = pids_str.split(",")
                    if len(pids) != ps_len // 2:
                        return HttpResponseBadRequest(
                            "The number of plate ids must be the same with the number of points."
                        )
                else:
                    if pid_str:
                        pids = (ps_len // 2) * [int(pid_str)]
                    else:
                        pids = (ps_len // 2) * [None]

                for lat, lon, pid_ in zip(ps[1::2], ps[0::2], pids):
                    point_feature = pygplates.Feature()
                    point_feature.set_geometry(
                        pygplates.PointOnSphere(float(lat), float(lon))
                    )
                    point_feature.set_name(str(p_index))
                    if pid_:
                        point_feature.set_reconstruction_plate_id(int(pid_))
                    point_features.append(point_feature)
                    p_index += 1
            except pygplates.InvalidLatLonError as e:
                return HttpResponseBadRequest(
                    "Invalid longitude or latitude ({0}).".format(e)
                )
            except ValueError as e:
                return HttpResponseBadRequest("Invalid value ({0}).".format(e))
        else:
            return HttpResponseBadRequest(
                "The longitude and latitude should come in pairs ({0}).".format(points)
            )
    else:
        return HttpResponseBadRequest('The "points" parameter is missing.')

    # assign plate-ids to points using static polygons
    partition_time = timef if is_reverse else 0.0

    if (
        not pids_str and not pid_str
    ):  # if user has provided plate id(s), do not partition(slow)
        # from time import time
        # start = time()

        # LOOK HERE !!!!
        # it seems when the partition_time is not 0
        # the returned assigned_point_features contains reverse reconstructed present-day geometries.
        # so, when doing reverse reconstruct, do not reverse reconstruct again later.
        assigned_point_features = pygplates.partition_into_plates(
            static_polygons_filename,
            rotation_model,
            point_features,
            properties_to_copy=[
                pygplates.PartitionProperty.reconstruction_plate_id,
                pygplates.PartitionProperty.valid_time_period,
            ],
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
                ret["coordinates"].append(None)  # return null for invalid coordinates
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
