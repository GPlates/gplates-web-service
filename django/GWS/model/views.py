from io import StringIO

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from utils.model_utils import (
    get_layer,
    get_rotation_model,
    get_static_polygons,
    get_topologies,
)

# Create your views here.


def index(request):
    return render(request, "list.html", {})


@csrf_exempt
def get_model_layer(request):
    # returns the source gpmlz file for a given model and layer name
    # regardless of the filename in the data store, the returned files will have
    # a name that reflects the official 'Name' used in the model specification string
    # currently file are always returned as gpmlz to minimise the size of files being transferred

    model = request.GET.get("model", settings.MODEL_DEFAULT)
    layer = request.GET.get("layer", "rotations")

    if layer == "rotations":
        target_feature_filename = "%s.rot" % model

        tmp = get_rotation_model(model)
        tmp.write(
            "%s/%s"
            % (settings.MEDIA_ROOT, target_feature_filename.encode("utf8", "ignore"))
        )
        f = StringIO(
            file("%s/%s" % (settings.MEDIA_ROOT, target_feature_filename), "rb").read()
        )

    elif layer == "static_polygons":
        target_feature_filename = "%s.gpmlz" % model
        tmp = get_static_polygons(model)
        tmp.write(
            "%s/%s"
            % (settings.MEDIA_ROOT, target_feature_filename.encode("utf8", "ignore"))
        )
        f = StringIO(
            file("%s/%s" % (settings.MEDIA_ROOT, target_feature_filename), "rb").read()
        )

    elif layer == "coastlines":
        target_feature_filename = "%s.gpmlz" % model
        tmp = get_layer("Coastlines")
        tmp.write(
            "%s/%s"
            % (settings.MEDIA_ROOT, target_feature_filename.encode("utf8", "ignore"))
        )
        f = StringIO(
            file("%s/%s" % (settings.MEDIA_ROOT, target_feature_filename), "rb").read()
        )

    elif layer == "plate_polygons":
        target_feature_filename = "%s.gpmlz" % model
        tmp = get_topologies(model)
        tmp.write(
            "%s/%s"
            % (settings.MEDIA_ROOT, target_feature_filename.encode("utf8", "ignore"))
        )
        f = StringIO(
            file("%s/%s" % (settings.MEDIA_ROOT, target_feature_filename), "rb").read()
        )

    else:
        return HttpResponseBadRequest("Unrecognised layer name: %s" % layer)

    response = HttpResponse(f, content_type="application/gpmlz")
    response["Content-Disposition"] = (
        "attachment; filename=%s" % target_feature_filename
    )

    return response
