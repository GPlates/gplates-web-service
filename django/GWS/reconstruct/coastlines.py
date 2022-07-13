from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings

from utils.get_model import get_reconstruction_model_dict, is_time_valid_model
from utils import wrapping_tools
from utils.round_float import round_floats
from utils import plot_geometries

import json, io
import pygplates

# @request_access
def get_coastline_polygons_low(request):
    return get_coastline_polygons(request)


def get_coastline_polygons(request):
    """
    http GET request to retrieve reconstructed coastline polygons

    **usage**

    <http-address-to-gws>/reconstruct/coastlines/plate_id=\ *anchor_plate_id*\&time=\ *reconstruction_time*\&model=\ *reconstruction_model*

    **parameters:**

    *anchor_plate_id* : integer value for reconstruction anchor plate id [default=0]

    *time* : time for reconstruction [required]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    *fmt* : if set this parameter to "png", this function will return a png image

    *facecolor* : such as "black", "blue", etc

    *edgecolor* : such as "black", "blue", etc

    *alpha* : such as 1, 0.5, etc

    *extent* : such as extent=-20,20,-20,20

    **returns:**

    json containing reconstructed coastline features
    """

    anchor_plate_id = request.GET.get("pid", 0)
    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    return_format = request.GET.get("fmt", "")
    edgecolor = request.GET.get("edgecolor", "black")
    facecolor = request.GET.get("facecolor", "none")
    alpha = request.GET.get("alpha", 0.5)
    extent = request.GET.get("extent", None)

    # parse the extent = [minx, maxx, miny, maxy]
    if extent:
        try:
            tmp = extent.split(",")
            extent = [float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3])]
        except:
            extent = None
            print("Invalid extent parameter!")

    wrap = True
    central_meridian = 0
    if "central_meridian" in request.GET:
        try:
            central_meridian = float(request.GET["central_meridian"])
            wrap = True
        except:
            print("Invalid central meridian.")

    avoid_map_boundary = False
    if "avoid_map_boundary" in request.GET:
        avoid_map_boundary = True

    model_dict = get_reconstruction_model_dict(model)

    if not is_time_valid_model(model_dict, time):
        return HttpResponseBadRequest(
            "Requested time %s not available for model %s" % (time, model)
        )

    rotation_model = pygplates.RotationModel(
        [
            str("%s/%s/%s" % (settings.MODEL_STORE_DIR, model, rot_file))
            for rot_file in model_dict["RotationFile"]
        ]
    )

    # reconstruct the coastlines
    reconstructed_polygons = []
    pygplates.reconstruct(
        str("%s/%s/%s" % (settings.MODEL_STORE_DIR, model, model_dict["Coastlines"])),
        rotation_model,
        reconstructed_polygons,
        float(time),
        anchor_plate_id=anchor_plate_id,
    )

    if extent:
        # extent = [minx, maxx, miny, maxy]
        extent_polygon = pygplates.PolygonOnSphere(
            [
                (extent[0], extent[2]),
                (extent[0], extent[3]),
                (extent[1], extent[3]),
                (extent[1], extent[2]),
            ]
        )

        reconstructed_polygons = filter(
            lambda reconstructed_polygon: 0
            == pygplates.GeometryOnSphere.distance(
                extent_polygon,
                reconstructed_polygon.get_reconstructed_geometry(),
                geometry1_is_solid=True,
                geometry2_is_solid=True,
            ),
            reconstructed_polygons,
        )

    # wrap=False #for debug

    # plot and return the map
    if return_format == "png":
        if wrap:
            date_line_wrapper = pygplates.DateLineWrapper(central_meridian)
        else:
            date_line_wrapper = None
        imgdata = plot_geometries.plot_polygons(
            reconstructed_polygons,
            edgecolor,
            facecolor,
            alpha,
            date_line_wrapper,
            extent,
        )
        return HttpResponse(imgdata, content_type="image/png")

    data = wrapping_tools.get_json_from_reconstructed_polygons(
        reconstructed_polygons, wrap, central_meridian, avoid_map_boundary
    )

    ret = json.dumps(round_floats(data))

    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
