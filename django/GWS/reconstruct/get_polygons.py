from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings

from utils.model_utils import get_reconstruction_model_dict, is_time_valid_model
from utils import wrapping_tools
from utils.round_float import round_floats
from utils import plot_geometries

import json
import pygplates


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
    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    return_format = request.GET.get("fmt", "")
    edgecolor = request.GET.get("edgecolor", "black")
    facecolor = request.GET.get("facecolor", "none")
    alpha = request.GET.get("alpha", 0.5)
    extent = request.GET.get("extent", None)
    wrap_str = request.GET.get("wrap", "true")

    if wrap_str.lower() == "false":
        wrap = False
    else:
        wrap = True

    # parse the extent = [minx, maxx, miny, maxy]
    if extent:
        try:
            tmp = extent.split(",")
            extent = [float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3])]
        except:
            extent = None
            print("Invalid extent parameter!")

    central_meridian = 0
    if "central_meridian" in request.GET:
        try:
            central_meridian = float(request.GET["central_meridian"])
        except:
            wrap = False
            print("Invalid central meridian.")

    avoid_map_boundary = False
    if "avoid_map_boundary" in request.GET:
        avoid_map_boundary = True

    model_dict = get_reconstruction_model_dict(model)

    if not is_time_valid_model(model_dict, time):
        return HttpResponseBadRequest(
            f"Requested time {time} not available for model {model}"
        )

    rotation_model = pygplates.RotationModel(
        [
            f"{settings.MODEL_STORE_DIR}/{model}/{rot_file}"
            for rot_file in model_dict["RotationFile"]
        ]
    )

    reconstructed_polygons = []
    fn = model_dict[polygon_name]
    pygplates.reconstruct(
        f"{settings.MODEL_STORE_DIR}/{model}/{fn}",
        rotation_model,
        reconstructed_polygons,
        float(time),
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

    # plot and return the map
    if return_format == "png":
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
        data = wrapping_tools.get_json_from_reconstructed_polygons(
            reconstructed_polygons, wrap, central_meridian, avoid_map_boundary
        )

        response = HttpResponse(
            json.dumps(round_floats(data)), content_type="application/json"
        )

    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
