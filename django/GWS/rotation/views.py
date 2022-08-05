import json

import numpy as np
import pygplates
from django.conf import settings
from django.http import HttpResponse
from utils.model_utils import get_reconstruction_model_dict
from utils.round_float import round_floats
from utils.wrapping_tools import wrap_polylines


def reconstruction_tree_map(request):
    """
    http GET request to retrieve a geographical representation of a reconstruction hierarchy

    **usage**

    <http-address-to-gws>/rotation/reconstruction_tree_map/time=\ *reconstruction_time*\&model=\ *reconstruction_model*

    **parameters:**

    *time* : time for reconstruction [required]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    **returns:**

    json containing reconstructed feature collection with a geometry representing the rotation hierarchy in a
    geographical arrangement
    """

    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel(
        [
            str("%s/%s/%s" % (settings.MODEL_STORE_DIR, model, rot_file))
            for rot_file in model_dict["RotationFile"]
        ]
    )

    static_polygons_filename = str(
        "%s/%s/%s" % (settings.MODEL_STORE_DIR, model, model_dict["StaticPolygons"])
    )

    tree = rotation_model.get_reconstruction_tree(float(time))

    edges = tree.get_edges()

    # Get a list of plate pairs
    tree_list = []
    for edge in edges:
        if edge.get_parent_edge() is not None:
            tree_list.append(
                (edge.get_fixed_plate_id(), edge.get_parent_edge().get_fixed_plate_id())
            )

    # get unique list (remove duplicates)
    uniq = list(set(tree_list))

    # Print a list of unique plate-pairs....
    print(uniq)

    rsp = []
    pygplates.reconstruct(static_polygons_filename, rotation_model, rsp, float(time))

    tree_features = []

    for plate_pair in uniq:
        p0 = GetPolygonCentroid(rsp, plate_pair[0])
        p1 = GetPolygonCentroid(rsp, plate_pair[1])

        if (len(p0) > 0) & (len(p1) > 0):

            feature = pygplates.Feature()
            simple_line = pygplates.PolylineOnSphere([p0, p1])
            feature.set_geometry(simple_line.to_tessellated(np.radians(1)))
            feature.set_shapefile_attribute("MovingPlate", plate_pair[0])
            feature.set_shapefile_attribute("FixedPlate", plate_pair[1])
            tree_features.append(feature)

    data = wrap_polylines(tree_features, 0.0)

    ret = json.dumps(round_floats(data))

    return HttpResponse(ret, content_type="application/json")

    # tree_feature_collection = pygplates.FeatureCollection(tree_features)
    # tree_feature_collection.write('tree.gmt')
    # response = HttpResponse(content_type='text/gmt')
    # response['Content-Disposition'] = 'attachment; filename="tree.gmt"'
    # return response


#########################################################################
# function to get centroid from every polygon in the reconstructed static polygons
def GetPolygonCentroid(static_polygons, plateid):
    centroid = []
    target_polygon_area = 0
    for polygon in static_polygons:
        if polygon.get_feature().get_reconstruction_plate_id() == plateid:
            if polygon.get_reconstructed_geometry() is not None:
                if (
                    polygon.get_reconstructed_geometry().get_area()
                    > target_polygon_area
                ):
                    centroid = (
                        polygon.get_reconstructed_geometry()
                        .get_boundary_centroid()
                        .to_lat_lon()
                    )
                    target_polygon_area = (
                        polygon.get_reconstructed_geometry().get_area()
                    )

    return centroid
