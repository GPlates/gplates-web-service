import json
from io import StringIO

import pandas as pd
import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from utils.kinematic_tools import subduction_parameters
from utils.plate_model_utils import get_rotation_model, get_static_polygons
from utils.reconstruct_tools import reconstruct_to_birth_time


class PrettyFloat(float):
    def __repr__(self):
        return "%.2f" % self


def pretty_floats(obj):
    if isinstance(obj, float):
        return PrettyFloat(obj)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in list(obj.items()))
    elif isinstance(obj, (list, tuple)):
        return list(map(pretty_floats, obj))
    return obj


@csrf_exempt
def test_post(request):
    if not request.method == "POST":
        return HttpResponseBadRequest("expecting post requests!")
    else:
        # print request.POST
        json_feature_collection = json.loads(request.body)

        model = request.GET.get("model", settings.MODEL_DEFAULT)

        features = []
        for json_feature in json_feature_collection["features"]:
            feature = pygplates.Feature()
            point = json_feature["geometry"]["coordinates"]
            feature.set_geometry(pygplates.PointOnSphere(point[1], point[0]))
            feature.set_valid_time(json_feature["properties"]["age"], 0)
            features.append(feature)

        

        rotation_model = get_rotation_model(model)

        \
        # assign plate-ids to points using static polygons
        assigned_point_features = pygplates.partition_into_plates(
            get_static_polygons(model),
            rotation_model,
            features,
            properties_to_copy=[pygplates.PartitionProperty.reconstruction_plate_id],
        )

        feature_collection = pygplates.FeatureCollection(assigned_point_features)

        reconstructed_features = reconstruct_to_birth_time(
            feature_collection, rotation_model
        )

        # prepare the response to be returned
        ret = '{"coordinates":['
        for g in reconstructed_features:
            ret += "[{0:5.2f},{1:5.2f}],".format(
                g.get_geometry().to_lat_lon()[1], g.get_geometry().to_lat_lon()[0]
            )
        ret = ret[0:-1]
        ret += "]}"
        return HttpResponse(ret, content_type="application/json")

        # for chunk in request.FILES['file'].chunks():
        #    data.append(chunk)
        #    #print chunk

        # print data
        # return HttpResponse("OK")


@csrf_exempt
def test_post_files(request):
    if not request.method == "POST":
        return HttpResponseBadRequest("expecting post requests!")
    else:
        with open("%s/tmp.gpmlz" % settings.MEDIA_ROOT, "wb+") as destination:
            for chunk in request.FILES["file1"].chunks():
                destination.write(chunk)
        with open("%s/tmp.rot" % settings.MEDIA_ROOT, "wb+") as destination:
            for chunk in request.FILES["file2"].chunks():
                destination.write(chunk)

        filename = "reconstruct_to_birth_time.gpmlz"
        rotation_model = pygplates.RotationModel("%s/tmp.rot" % settings.MEDIA_ROOT)
        features = pygplates.FeatureCollection("%s/tmp.gpmlz" % settings.MEDIA_ROOT)

        reconstructed_features = reconstruct_to_birth_time(features, rotation_model)

        tmp = pygplates.FeatureCollection(reconstructed_features)
        tmp.write("%s/%s" % (settings.MEDIA_ROOT, filename))

        f = StringIO(file("%s/%s" % (settings.MEDIA_ROOT, filename), "rb").read())

        response = HttpResponse(f, content_type="application/gpmlz")
        response["Content-Disposition"] = "attachment; filename=%s" % filename

        return response


@csrf_exempt
def html_model_list(request):
    df = pd.read_csv(
        "%s/%s" % (settings.PALEO_STORE_DIR, "ngeo2429-s2.csv"),
        index_col="Deposit number",
    )
    html_table = df.to_html(index=False)
    return render(request, "list_template.html", {"html_table": html_table})


@csrf_exempt
def subduction(request):
    if not request.method == "POST":
        return HttpResponseBadRequest("expecting post requests!")
    else:
        # print request.POST
        json_feature_collection = json.loads(request.body)

        model = request.GET.get("model", settings.MODEL_DEFAULT)

        features = []
        for json_feature in json_feature_collection["features"]:
            feature = pygplates.Feature()
            point = json_feature["geometry"]["coordinates"]
            feature.set_geometry(pygplates.PointOnSphere(point[1], point[0]))
            feature.set_valid_time(json_feature["properties"]["age"], 0)
            features.append(feature)

        

        rotation_model = get_rotation_model(model)

        
        # assign plate-ids to points using static polygons
        assigned_point_features = pygplates.partition_into_plates(
            get_static_polygons(model),
            rotation_model,
            features,
            properties_to_copy=[pygplates.PartitionProperty.reconstruction_plate_id],
        )

        seed_point_features = pygplates.FeatureCollection(assigned_point_features)

        df_OreDepositBirthTimeStats = subduction_parameters(
            seed_point_features, rotation_model
        )

        html_table = df_OreDepositBirthTimeStats.to_html(index=False)
        return render(request, "list_template.html", {"html_table": html_table})
