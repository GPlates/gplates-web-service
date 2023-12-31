import json
import logging

import pygplates
import shapely
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from utils import parameter_helper, plot_geometries, wrapping_tools
from utils.access_control import get_client_ip
from utils.plate_model_utils import (
    get_layer,
    get_rotation_model,
    is_time_valid_for_model,
)
from utils.round_float import round_floats

logger = logging.getLogger("default")
access_logger = logging.getLogger("queue")


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
    """return reconstructed polygons in geojson or PNG formt

    :param polygon_name: two options for now - "StaticPolygons", "Coastlines"
    :param anchor_plate_id : integer value for reconstruction anchor plate id [default=0]
    :param time : time for reconstruction [required]
    :param model : name for reconstruction model [defaults to default model from web service settings]
    :param fmt : if set this parameter to "png", this function will return a png image
    :param facecolor : such as "black", "blue", etc
    :param edgecolor : such as "black", "blue", etc
    :param alpha : such as 1, 0.5, etc
    :param extent : such as extent=-180,180,-90,90
    :param central_meridian: central meridian
    :param wrap: flag to indicate if wrap the polygons along dateline

    """

    access_logger.info(get_client_ip(request) + f" {request.get_full_path()}")

    anchor_plate_id = parameter_helper.get_int(request.GET, "anchor_plate_id", 0)
    time = parameter_helper.get_float(request.GET, "time", 0.0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    return_format = request.GET.get("fmt", "")
    edgecolor = request.GET.get("edgecolor", "black")
    facecolor = request.GET.get("facecolor", "none")
    alpha = request.GET.get("alpha", 0.5)
    extent = request.GET.get("extent", None)
    wrap = parameter_helper.get_bool(request.GET, "wrap", True)
    min_area = parameter_helper.get_float(request.GET, "min_area", 0.0)
    central_meridian = parameter_helper.get_float(request.GET, "central_meridian", 0.0)

    # parse the extent = [minx, maxx, miny, maxy]
    if extent:
        try:
            tmp = extent.split(",")
            extent = [float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3])]
        except:
            extent = None
            logger.warn("Invalid extent parameter!")

    # check the avoid_map_boundary flag
    avoid_map_boundary = parameter_helper.get_bool(
        request.GET, "avoid_map_boundary", True
    )

    # validate time
    if not is_time_valid_for_model(model, time):
        msg = f"Requested time {time} not available for model {model}."
        logger.warn(msg)
        return HttpResponseBadRequest(msg)

    # do the reconstruction
    reconstructed_polygons = []
    pygplates.reconstruct(
        get_layer(model, polygon_name),
        get_rotation_model(model),
        reconstructed_polygons,
        time,
        anchor_plate_id=anchor_plate_id,
    )

    # filter the polygons by min_area
    if min_area > 0:
        tmp = []
        for polygon in reconstructed_polygons:
            p = polygon.get_reconstructed_geometry()
            try:
                if p.get_area() * (pygplates.Earth.mean_radius_in_kms**2) > min_area:
                    # logger.debug(p.get_area() * (pygplates.Earth.mean_radius_in_kms**2))
                    tmp.append(polygon)
            except:
                logger.warn("Invalid geometry type {p}")
        reconstructed_polygons = tmp

    shapely_polygons = []
    for polygon in reconstructed_polygons:
        if wrap:
            # wrap the polygons to dateline
            tesselate_degrees = 2
            date_line_wrapper = pygplates.DateLineWrapper(central_meridian)

            ps = date_line_wrapper.wrap(
                polygon.get_reconstructed_geometry(), tesselate_degrees
            )
            for p in ps:
                points = []
                for point in p.get_exterior_points():
                    lon = point.to_lat_lon()[1]
                    lat = point.to_lat_lon()[0]
                    # LOOK HERE!!!!!!
                    # https://www.gplates.org/docs/pygplates/generated/pygplates.datelinewrapper
                    # If central_meridian is non-zero then the dateline is essentially shifted
                    # such that the longitudes of the wrapped points lie in the range
                    # [central_meridian - 180, central_meridian + 180]. If central_meridian
                    # is zero then the output range becomes [-180, 180].
                    lon = lon - central_meridian
                    points.append([lon, lat])
                tp = shapely.Polygon(points).buffer(0)
                if isinstance(tp, shapely.MultiPolygon):
                    for pp in tp.geoms:
                        shapely_polygons.append(pp)
                else:
                    shapely_polygons.append(tp)
        else:
            tp = shapely.Polygon(
                [
                    (p[1], p[0])
                    for p in polygon.get_reconstructed_geometry().to_lat_lon_list()
                ]
            ).buffer(0)
            if isinstance(tp, shapely.MultiPolygon):
                for pp in tp.geoms:
                    shapely_polygons.append(pp)
            else:
                shapely_polygons.append(tp)

    if extent:
        # clip the geometries with the bounding box
        # extent = [minx, maxx, miny, maxy]
        tmp = []
        shapely_box = shapely.Polygon(
            [
                (extent[0], extent[3]),
                (extent[0], extent[2]),
                (extent[1], extent[2]),
                (extent[1], extent[3]),
                (extent[0], extent[3]),
            ]
        )
        for shapely_polygon in shapely_polygons:
            if not shapely_polygon.is_simple:
                continue
            tmp_p = shapely_box.intersection(shapely_polygon)
            if tmp_p.is_empty:
                continue
            if isinstance(tmp_p, shapely.Polygon):
                tmp.append(tmp_p)
            elif isinstance(tmp_p, shapely.MultiPolygon):
                for p in tmp_p.geoms:
                    tmp.append(p)
        shapely_polygons = tmp

    shapely_polygons = [shapely.geometry.polygon.orient(p) for p in shapely_polygons]

    if return_format == "png":
        # plot and return the map
        imgdata = plot_geometries.plot_polygons(
            shapely_polygons,
            edgecolor,
            facecolor,
            alpha,
            extent=extent,
            central_meridian=central_meridian,
        )
        response = HttpResponse(imgdata, content_type="image/png")
    else:
        # prepare and return in geojson format
        data = wrapping_tools.get_json_from_shapely_polygons(
            shapely_polygons, avoid_map_boundary
        )
        # logger.debug(len(shapely_polygons))
        response = HttpResponse(
            json.dumps(round_floats(data)), content_type="application/json"
        )

    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
