import json

import pygplates
from django.conf import settings
from django.http import HttpResponse
from utils.geojson_io import dump_geojson
from utils.plate_model_utils import get_rotation_model, get_topologies
from utils.round_float import round_floats


def get_subduction_zones(request):
    """return subduction zones as polylines"""

    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    resolved_topologies = []
    shared_boundary_sections = []
    pygplates.resolve_topologies(
        get_topologies(model),
        get_rotation_model(model),
        resolved_topologies,
        float(time),
        shared_boundary_sections,
    )

    subduction_features_with_no_polarity = []
    subduction_features_left = []
    subduction_features_right = []
    for shared_boundary_section in shared_boundary_sections:
        if (
            shared_boundary_section.get_feature().get_feature_type()
            == pygplates.FeatureType.gpml_subduction_zone
        ):
            boundary_section_features = [
                shared_sub_segment.get_resolved_feature()
                for shared_sub_segment in shared_boundary_section.get_shared_sub_segments()
            ]

            polarity_property = shared_boundary_section.get_feature().get(
                pygplates.PropertyName.create_gpml("subductionPolarity")
            )
            if polarity_property:
                polarity = polarity_property.get_value().get_content()
                if polarity == "Left":
                    subduction_features_left.extend(boundary_section_features)
                elif polarity == "Right":
                    subduction_features_right.extend(boundary_section_features)
                else:
                    subduction_features_with_no_polarity.extend(
                        boundary_section_features
                    )

    data = {"type": "FeatureCollection"}
    geoms = [f.get_geometry() for f in subduction_features_with_no_polarity]
    subduction_no_polarity = dump_geojson(geoms)

    geoms = [f.get_geometry() for f in subduction_features_left]
    list_of_polarity = [{"polarity": "left"}] * len(subduction_features_left)
    subduction_left = dump_geojson(geoms, list_of_properties=list_of_polarity)

    geoms = [f.get_geometry() for f in subduction_features_right]
    list_of_polarity = [{"polarity": "right"}] * len(subduction_features_right)
    subduction_right = dump_geojson(geoms, list_of_properties=list_of_polarity)

    data["features"] = subduction_no_polarity + subduction_left + subduction_right

    ret = json.dumps(round_floats(data))

    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
