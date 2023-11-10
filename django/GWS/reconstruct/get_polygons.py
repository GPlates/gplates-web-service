import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from utils import parameter_helper, plot_geometries, wrapping_tools
from utils.model_utils import get_layer, get_rotation_model, is_time_valid_for_model
from utils.round_float import round_floats


# @request_access
def get_coastline_polygons_low(request):
    return get_coastline_polygons(request)


def get_coastline_polygons(request):
    """http GET request to retrieve reconstructed coastline polygons
    see this link for how to use https://gwsdoc.gplates.org/reconstruction/reconstruct-coastlines

    """
    return get_polygons(request, "Coastlines")


#
# http GET request to retrieve reconstructed static polygons
# see this link for how to use https://gwsdoc.gplates.org/reconstruction/reconstruct-static-polygons
#
def get_static_polygons(request):
    """http GET request to retrieve reconstructed static polygons
    see this link for how to use https://gwsdoc.gplates.org/reconstruction/reconstruct-static-polygons

    """
    return get_polygons(request, "StaticPolygons")


def get_polygons(request, polygon_name):
    """return reconstructed polygons in JSON or PNG formt

    :param anchor_plate_id : integer value for reconstruction anchor plate id [default=0]
    :param  time : time for reconstruction [required]
    :param  model : name for reconstruction model [defaults to default model from web service settings]
    :param  fmt : if set this parameter to "png", this function will return a png image
    :param  facecolor : such as "black", "blue", etc
    :param  edgecolor : such as "black", "blue", etc
    :param  alpha : such as 1, 0.5, etc
    :param  extent : such as extent=-180,180,-90,90
    :param central_meridian: central meridian
    :param wrap: flag to indicate if wrap the polygons along dateline

    """
    anchor_plate_id = request.GET.get("pid", 0)
    time = parameter_helper.get_float(request.GET, "time", 0.0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    return_format = request.GET.get("fmt", "")
    edgecolor = request.GET.get("edgecolor", "black")
    facecolor = request.GET.get("facecolor", "none")
    alpha = request.GET.get("alpha", 0.5)
    extent = request.GET.get("extent", None)
    wrap_str = request.GET.get("wrap", "true")

    min_area = parameter_helper.get_float(request.GET, "min_area")

    if wrap_str.lower() == "false":
        wrap = False
    else:
        wrap = True

    central_meridian = parameter_helper.get_float(request.GET, "central_meridian", 0.0)

    # parse the extent = [minx, maxx, miny, maxy]
    if extent:
        try:
            tmp = extent.split(",")
            extent = [float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3])]
        except:
            extent = None
            print("Invalid extent parameter!")

    # check the avoid_map_boundary flag
    if (
        "avoid_map_boundary" in request.GET
        and request.GET["avoid_map_boundary"].lower() == "false"
    ):
        avoid_map_boundary = False
    else:
        avoid_map_boundary = True

    # validate time
    if not is_time_valid_for_model(model, time):
        return HttpResponseBadRequest(
            f"Requested time {time} not available for model {model}"
        )

    # do the reconstruction
    reconstructed_polygons = []
    pygplates.reconstruct(
        get_layer(model, polygon_name),
        get_rotation_model(model),
        reconstructed_polygons,
        time,
        anchor_plate_id=anchor_plate_id,
    )

    if extent:
        # filter the geometries with the bounding box
        # extent = [minx, maxx, miny, maxy]
        tmp = []
        for polygon in reconstructed_polygons:
            all_points = polygon.get_reconstructed_geometry().to_lat_lon_list()
            lats = [p[0] for p in all_points]
            lons = [p[0] for p in all_points]
            max_lat = max(lats)
            min_lat = min(lats)
            max_lon = max(lons)
            min_lon = min(lons)
            if (
                max_lon < extent[0]
                or min_lon > extent[1]
                or max_lat < extent[2]
                or min_lat > extent[3]
            ):
                continue
            else:
                tmp.append(polygon)
        reconstructed_polygons = tmp

    # filter the polygons by min_area
    if min_area is not None and min_area > 0:
        tmp = []
        for polygon in reconstructed_polygons:
            p = polygon.get_reconstructed_geometry()
            try:
                if p.get_area() * (pygplates.Earth.mean_radius_in_kms**2) > min_area:
                    tmp.append(polygon)
            except:
                print("Invalid geometry type {p}")
        reconstructed_polygons = tmp

    if return_format == "png":
        # plot and return the map
        imgdata = plot_geometries.plot_polygons(
            reconstructed_polygons,
            edgecolor,
            facecolor,
            alpha,
            extent=extent,
            central_meridian=central_meridian,
        )
        response = HttpResponse(imgdata, content_type="image/png")
    else:
        # prepare and return in geojson format
        data = wrapping_tools.get_json_from_reconstructed_polygons(
            reconstructed_polygons, wrap, central_meridian, avoid_map_boundary
        )

        response = HttpResponse(
            json.dumps(round_floats(data)), content_type="application/json"
        )

    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
