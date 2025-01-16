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
def get_plate_polygons(_, model="", times=[], params={}):
    """http GET request handlere for /topology/plate_polygons
    to retrieve reconstructed topological plate polygons

    http://localhost:18000/topology/plate_polygons?time=100&model=Muller2019

    :params time: time for reconstruction
    :params model: name for the reconstruction model (if not specified, will use the default model)

    :returns: json containing reconstructed plate polygon features
    """
    time = times[0]
    central_meridian = params.get("central_meridian", 0)
    as_lines = params.get("as_lines", False)

    if isinstance(as_lines, str) and as_lines.lower() in ["true", "1"]:
        as_lines = True

    resolved_topologies = []
    pygplates.resolve_topologies(
        get_topologies(model),
        get_rotation_model(model),
        resolved_topologies,
        float(time),
        # resolve_topology_types=pygplates.ResolveTopologyType.boundary,
    )

    geometries = []
    properties = []
    for topology in resolved_topologies:
        f = topology.get_resolved_feature()
        # print(f.get_name())
        logger.debug(f.get_feature_type())
        geoms = f.get_geometries()
        if as_lines:
            geoms = [pygplates.PolylineOnSphere(g) for g in geoms]
        geometries.extend(geoms)
        p = {
            "type": str(f.get_feature_type()),
            "name": f.get_name(),
            "pid": f.get_reconstruction_plate_id(),
        }
        properties.extend([p] * len(geoms))

    data = {"type": "FeatureCollection"}
    data["features"] = dump_geojson(
        geometries,
        list_of_properties=properties,
        date_line_wrapper=pygplates.DateLineWrapper(central_meridian),
    )

    return json.dumps(round_floats(data))
