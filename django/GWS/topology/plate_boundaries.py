import json
import logging

import pygplates
from utils.decorators import (
    extract_model_and_times,
    extract_params_GET_only,
    return_HttpResponse,
)
from utils.geojson_io import dump_geojson
from utils.plate_model_utils import get_rotation_model, get_topologies
from utils.round_float import round_floats

logger = logging.getLogger("default")


@extract_params_GET_only
@extract_model_and_times
@return_HttpResponse()
def get_topological_boundaries(_, model="", times=[], params={}):
    """http GET request handler for topology/plate_boundaries
    to retrieve reconstructed topological plate boundaries as polylines

    http://localhost:18000/topology/plate_boundaries?time=100&model=Muller2019

    :params time: time for reconstruction
    :params model: name for the reconstruction model (if not specified, will use the default model)

    :returns: json containing reconstructed plate boundary polylines
    """

    time = times[0]
    central_meridian = params.get("central_meridian", 0)

    resolved_polygons = []
    shared_boundary_sections = []
    pygplates.resolve_topologies(
        get_topologies(model),
        get_rotation_model(model),
        resolved_polygons,
        float(time),
        shared_boundary_sections,
        resolve_topology_types=pygplates.ResolveTopologyType.boundary,
    )

    geometries = []
    list_of_properties = []
    for shared_boundary_section in shared_boundary_sections:
        for shared_sub_segment in shared_boundary_section.get_shared_sub_segments():
            geom = shared_sub_segment.get_geometry()
            feat = shared_sub_segment.get_feature()
            feature_type = feat.get_feature_type()
            geometries.append(geom)
            p = {
                "type": feature_type.get_name(),
                "length": geom.get_arc_length(),
                "pid": feat.get_reconstruction_plate_id(),
                "name": feat.get_name(),
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

    return json.dumps(round_floats(data))
