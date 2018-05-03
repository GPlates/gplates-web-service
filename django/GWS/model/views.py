from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect

# Create your views here.

from StringIO import StringIO
import numpy as np
import pygplates
from utils.get_model import get_reconstruction_model_dict


def index(request):
    return render(
        request,
        'list.html',
        {}
    )


@csrf_exempt
def get_model_layer(request):

    # returns the source gpmlz file for a given model and layer name
    # regardless of the filename in the data store, the returned files will have 
    # a name that reflects the official 'Name' used in the model specification string
    # currently file are always returned as gpmlz to minimise the size of files being transferred

    model = request.GET.get('model',settings.MODEL_DEFAULT)
    layer = request.GET.get('layer','rotations')

    model_dict = get_reconstruction_model_dict(model)

    if layer=='rotations':
        target_feature_filename = '%s.rot' % model

        tmp = pygplates.FeatureCollection()
        for rot_file in model_dict['RotationFile']:
            tmp.add(pygplates.FeatureCollection(str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,rot_file))))

        tmp.write('%s/%s' % (settings.MEDIA_ROOT,target_feature_filename.encode("utf8","ignore")))
        f = StringIO(file('%s/%s' % (settings.MEDIA_ROOT,target_feature_filename), "rb").read())

    elif layer=='static_polygons':
        target_feature_filename = '%s.gpmlz' % model
        tmp = pygplates.FeatureCollection(str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons'])))
        tmp.write('%s/%s' % (settings.MEDIA_ROOT,target_feature_filename))
        f = StringIO(file('%s/%s' % (settings.MEDIA_ROOT,target_feature_filename), "rb").read())

    elif layer=='coastlines':
        target_feature_filename = '%s.gpmlz' % model
        tmp = pygplates.FeatureCollection(str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['Coastlines'])))
        tmp.write('%s/%s' % (settings.MEDIA_ROOT,target_feature_filename))
        f = StringIO(file('%s/%s' % (settings.MEDIA_ROOT,target_feature_filename), "rb").read())

    elif layer=='plate_polygons':
        target_feature_filename = '%s.gpmlz' % model
        tmp = pygplates.FeatureCollection()
        for gpmlfile in model_dict['PlatePolygons']:
            tmp.add(pygplates.FeatureCollection(str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,gpmlfile))))

        tmp.write('%s/%s' % (settings.MEDIA_ROOT,target_feature_filename))
        f = StringIO(file('%s/%s' % (settings.MEDIA_ROOT,target_feature_filename), "rb").read())

    else:
        return HttpResponseBadRequest('Unrecognised layer name: %s' % layer)
    
    
    response = HttpResponse(f, content_type = 'application/gpmlz')
    response['Content-Disposition'] = 'attachment; filename=%s' % target_feature_filename

    return response
