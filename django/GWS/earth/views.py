from io import StringIO

import numpy as np
import pygplates
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from utils.create_gpml import create_gpml_crustal_thickness
from utils.fileio import write_json_reconstructed_point_features
from utils.plate_model_utils import get_rotation_model, get_static_polygons
from utils.sphere_tools import healpix_mesh, random_points_on_sphere, sampleOnSphere

# Create your views here.


@csrf_exempt
def litho1(request):
    mode = request.GET.get("mode", "random_points")
    filename = request.GET.get("filename", "litho1_scalar_coverage.gpmlz")
    if mode == "healpix":
        Nstr = request.GET.get("N", 64)
    else:
        Nstr = request.GET.get("N", 100000)

    N = int(Nstr)

    data = np.loadtxt(
        "%s/litho1.0_CrustThickness.csv" % settings.EARTH_STORE_DIR, delimiter=","
    )

    if mode == "healpix":
        longitude_array, latitude_array = healpix_mesh(N)
    else:
        longitude_array, latitude_array = random_points_on_sphere(N)

    d, l = sampleOnSphere(
        data[:, 1], data[:, 0], data[:, 2], latitude_array, longitude_array, n=4
    )

    interp_thickness = data[:, 2].ravel()[l]

    create_gpml_crustal_thickness(
        longitude_array, latitude_array, interp_thickness, filename
    )

    f = StringIO(file(filename, "rb").read())

    response = HttpResponse(f, content_type="application/gpmlz")
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    # response['Content-Length'] = filename.tell()

    return response


@csrf_exempt
def paleolithology(request):
    anchor_plate_id = request.GET.get("pid", 0)
    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    rotation_model = get_rotation_model(model)

    paleolithology_datafile = (
        "%s/boucot_paleolithology_combined.shp" % settings.PALEO_STORE_DIR
    )

    # select points based on age before doing plate id assignment - should be quicker??
    paleolithology_points = pygplates.FeatureCollection(paleolithology_datafile)

    valid_points = []
    for point in paleolithology_points:
        if point.get_valid_time()[0] > float(time) and point.get_valid_time()[
            1
        ] <= float(time):
            valid_points.append(point)

    print(valid_points)

    assigned_features = pygplates.partition_into_plates(
        get_static_polygons(),
        rotation_model,
        valid_points,
        properties_to_copy=[pygplates.PartitionProperty.reconstruction_plate_id],
        partition_method=pygplates.PartitionMethod.most_overlapping_plate,
    )

    reconstructed_paleolithology_points = []
    pygplates.reconstruct(
        assigned_features,
        rotation_model,
        reconstructed_paleolithology_points,
        float(time),
        anchor_plate_id=anchor_plate_id,
    )

    ret = write_json_reconstructed_point_features(
        reconstructed_paleolithology_points,
        attributes=[("LithCode", "string"), ("Period", "string")],
    )

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type="application/json")

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response


@csrf_exempt
def paleomagnetic_poles(request):
    anchor_plate_id = request.GET.get("pid", 0)
    time = request.GET.get("time", 0)
    model = request.GET.get("model", settings.MODEL_DEFAULT)

    rotation_model = get_rotation_model(model)

    vgp_datafile = "%s/T2012_VGPs.gpmlz" % settings.PALEO_STORE_DIR

    # select points based on age before doing plate id assignment - should be quicker??
    vgp_points = pygplates.FeatureCollection(vgp_datafile)

    # valid_points = []
    # for point in vgp_points:
    #    if point.get_valid_time()[0]>time and point.get_valid_time()[1]<time:
    #        valid_points.append(point)

    assigned_features = pygplates.partition_into_plates(
        get_static_polygons(),
        rotation_model,
        vgp_points,
        properties_to_copy=[pygplates.PartitionProperty.reconstruction_plate_id],
        partition_method=pygplates.PartitionMethod.most_overlapping_plate,
    )

    reconstructed_vgps = []
    pygplates.reconstruct(
        assigned_features,
        rotation_model,
        reconstructed_vgps,
        float(time),
        anchor_plate_id=anchor_plate_id,
    )

    ret = write_json_reconstructed_point_features(reconstructed_vgps, attributes=None)

    # add header for CORS
    # http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type="application/json")

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
