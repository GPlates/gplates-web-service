import json

import pygplates
from django.conf import settings
from django.http import HttpResponse
from utils.geojson_io import dump_geojson
from utils.model_utils import get_rotation_model, get_topologies
from utils.round_float import round_floats


def get_plate_polygons(request):
    """http GET request to retrieve reconstructed topological plate polygons

    http://localhost:18000/topology/plate_polygons?time=100&model=Muller2019

    :params time: time for reconstruction [default=0]
    :params model: name for reconstruction model [defaults to default model from web service settings]

    :returns: json containing reconstructed plate polygon features
    """

    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    central_meridian = request.GET.get("central_meridian", 0)
    as_lines = request.GET.get("as_lines", False)

    if isinstance(as_lines, str) and as_lines.lower() == "true":
        as_lines = True

    resolved_topologies = []
    pygplates.resolve_topologies(
        get_topologies(model),
        get_rotation_model(model),
        resolved_topologies,
        float(time),
    )

    geometries = []
    properties = []
    for topology in resolved_topologies:
        f = topology.get_resolved_feature()
        # print(f.get_name())
        if (
            f.get_feature_type()
            == pygplates.FeatureType.gpml_topological_closed_plate_boundary
        ):
            # print(f.get_feature_type())
            geoms = f.get_geometries()
            if as_lines:
                geoms = [pygplates.PolylineOnSphere(g.to_lat_lon_list()) for g in geoms]
            geometries.extend(geoms)
            properties.extend([{"name": f.get_name()}] * len(geoms))

    data = {"type": "FeatureCollection"}
    data["features"] = dump_geojson(
        geometries,
        list_of_properties=properties,
        date_line_wrapper=pygplates.DateLineWrapper(central_meridian),
    )

    response = HttpResponse(
        json.dumps(round_floats(data)), content_type="application/json"
    )
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_topological_boundaries(request):
    """http GET request to retrieve reconstructed topological plate boundaries

    http://localhost:18000/topology/plate_boundaries?time=100&model=Muller2019

    :params time: time for reconstruction [default=0]
    :params model: name for reconstruction model [defaults to default model from web service settings]

    :returns: json containing reconstructed plate boundary features
    """

    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    central_meridian = request.GET.get("central_meridian", 0)

    resolved_polygons = []
    shared_boundary_sections = []
    pygplates.resolve_topologies(
        get_topologies(model),
        get_rotation_model(model),
        resolved_polygons,
        float(time),
        shared_boundary_sections,
    )

    geometries = []
    list_of_properties = []
    for shared_boundary_section in shared_boundary_sections:
        for shared_sub_segment in shared_boundary_section.get_shared_sub_segments():
            geom = shared_sub_segment.get_geometry()
            feature_type = shared_sub_segment.get_feature().get_feature_type()
            geometries.append(geom)
            p = {
                "type": feature_type.get_name(),
                "length": geom.get_arc_length(),
            }
            if feature_type == pygplates.FeatureType.gpml_subduction_zone:
                polarity_property = shared_sub_segment.get_feature().get(
                    pygplates.PropertyName.create_gpml("subductionPolarity")
                )
                if polarity_property:
                    p["polarity"] = polarity_property.get_value().get_content()
                else:
                    p["polarity"] = "Unknown"

            list_of_properties.append(p)

    data = {"type": "FeatureCollection"}
    data["features"] = dump_geojson(
        geometries,
        list_of_properties=list_of_properties,
        date_line_wrapper=pygplates.DateLineWrapper(central_meridian),
    )

    ret = json.dumps(round_floats(data))

    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
