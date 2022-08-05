import json

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from utils.model_utils import get_reconstruction_model_dict
from utils.round_float import round_floats

#
# reconstruct geojson feature collection
#
@csrf_exempt
def reconstruct(request):

    if request.method == "POST":
        params = request.POST
    elif request.method == "GET":
        params = request.GET
    else:
        return HttpResponseBadRequest("Unrecognized request type")

    anchor_plate_id = params.get("pid", 0)

    if "time" in params:
        time = params["time"]
    elif "geologicage" in params:
        time = params["geologicage"]
    else:
        time = 140  # default reconstruction age

    output_format = params.get("output", "geojson")
    fc_str = params.get("feature_collection")
    model = str(params.get("model", settings.MODEL_DEFAULT))

    if "keep_properties" in params:
        keep_properties = True
    else:
        keep_properties = False

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
            'The "pid" parameter is invalid ({0}).'.format(anchor_plate_id)
        )

    # Convert geojson input to gplates feature collection
    features = []
    try:
        fc = json.loads(fc_str)  # load the input feature collection
        for f in fc["features"]:
            geom = f["geometry"]
            feature = pygplates.Feature()
            if geom["type"] == "Point":
                feature.set_geometry(
                    pygplates.PointOnSphere(
                        float(geom["coordinates"][1]), float(geom["coordinates"][0])
                    )
                )
            if geom["type"] == "LineString":
                feature.set_geometry(
                    pygplates.PolylineOnSphere(
                        [(point[1], point[0]) for point in geom["coordinates"]]
                    )
                )
            if geom["type"] == "Polygon":
                feature.set_geometry(
                    pygplates.PolygonOnSphere(
                        [(point[1], point[0]) for point in geom["coordinates"][0]]
                    )
                )
            if geom["type"] == "MultiPoint":
                feature.set_geometry(
                    pygplates.MultiPointOnSphere(
                        [(point[1], point[0]) for point in geom["coordinates"]]
                    )
                )

            if keep_properties and "properties" in f:
                for pk in f["properties"]:
                    p = f["properties"][pk]
                    if isinstance(p, str):
                        p = str(p)
                    feature.set_shapefile_attribute(str(pk), p)

            features.append(feature)
    except Exception as e:
        # print e
        return HttpResponseBadRequest("Invalid input feature collection")

    model_dict = get_reconstruction_model_dict(model)
    if not model_dict:
        return HttpResponseBadRequest(
            'The "model" ({0}) cannot be recognized.'.format(model)
        )

    rotation_model = pygplates.RotationModel(
        [
            str("%s/%s/%s" % (settings.MODEL_STORE_DIR, model, rot_file))
            for rot_file in model_dict["RotationFile"]
        ]
    )

    assigned_features = pygplates.partition_into_plates(
        settings.MODEL_STORE_DIR + model + "/" + model_dict["StaticPolygons"],
        rotation_model,
        features,
        properties_to_copy=[
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period,
        ],
        partition_method=pygplates.PartitionMethod.most_overlapping_plate,
    )

    reconstructed_geometries = []
    pygplates.reconstruct(
        assigned_features,
        rotation_model,
        reconstructed_geometries,
        timef,
        anchor_plate_id=anchor_plate_id,
    )

    # convert feature collection back to geojson
    data = {"type": "FeatureCollection"}
    data["features"] = []
    for g in reconstructed_geometries:
        geom = g.get_reconstructed_geometry()
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        if isinstance(geom, pygplates.PointOnSphere):
            feature["geometry"]["type"] = "Point"
            p = geom.to_lat_lon_list()[0]
            feature["geometry"]["coordinates"] = [p[1], p[0]]
        elif isinstance(geom, pygplates.MultiPointOnSphere):
            feature["geometry"]["type"] = "MultiPoint"
            feature["geometry"]["coordinates"] = [
                [lon, lat] for lat, lon in geom.to_lat_lon_list()
            ]
        elif isinstance(geom, pygplates.PolylineOnSphere):
            feature["geometry"]["type"] = "LineString"
            feature["geometry"]["coordinates"] = [
                [lon, lat] for lat, lon in geom.to_lat_lon_list()
            ]
        elif isinstance(geom, pygplates.PolygonOnSphere):
            feature["geometry"]["type"] = "Polygon"
            feature["geometry"]["coordinates"] = [
                [[lon, lat] for lat, lon in geom.to_lat_lon_list()]
            ]
        else:
            return HttpResponseServerError("Unsupported Geometry Type.")

        feature["properties"] = {}
        if keep_properties:
            for pk in g.get_feature().get_shapefile_attributes():
                feature["properties"][pk] = g.get_feature().get_shapefile_attribute(pk)
        # print feature["properties"]
        data["features"].append(feature)

    ret = json.dumps(round_floats(data))

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type="application/json")
    # TODO:
    response["Access-Control-Allow-Origin"] = "*"
    return response
