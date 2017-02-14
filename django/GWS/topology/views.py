from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings

import sys, json

from utils.get_model import get_reconstruction_model_dict
from utils.wrapping_tools import wrap_polygons, wrap_plate_boundaries

import pygplates


def index(request):
    return render(
        request,
        'list.html',
        {}
    )

class PrettyFloat(float):
    def __repr__(self):
        return '%.2f' % self

def pretty_floats(obj):
    if isinstance(obj, float):
        return PrettyFloat(obj)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_floats, obj)             
    return obj


def get_plate_polygons(request):
    """
    http GET request to retrieve reconstructed topological plate polygons

    **usage**
    
    <http-address-to-gws>/topology/plate_polygons/time=\ *reconstruction_time*\&model=\ *reconstruction_model*
    
    **parameters:**

    *time* : time for reconstruction [default=0]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    **returns:**

    json containing reconstructed plate polygon features
    """

    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)    

    #features = []
    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,model_dict['RotationFile'])))  

    resolved_polygons = []
    pygplates.resolve_topologies(
        str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['PlatePolygons'])),
        rotation_model, 
        resolved_polygons,
        float(time))
    
    resolved_features = []
    for polygon in resolved_polygons:
        resolved_features.append(polygon.get_resolved_feature())

    data = wrap_polygons(resolved_features,0.)
    
    ret = json.dumps(pretty_floats(data))
   
    return HttpResponse(ret, content_type='application/json')

def get_topological_boundaries(request):
    """
    http GET request to retrieve reconstructed topological plate polygons

    **usage**
    
    <http-address-to-gws>/topology/plate_boundaries/time=\ *reconstruction_time*\&model=\ *reconstruction_model*
    
    **parameters:**

    *time* : time for reconstruction [default=0]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    **returns:**

    json containing reconstructed plate boundary features
    """
    
    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)
    
    features = []
    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,model_dict['RotationFile'])))   

    resolved_polygons = []
    shared_boundary_sections = []
    pygplates.resolve_topologies(
        str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['PlatePolygons'])),
        rotation_model, 
        resolved_polygons,
        float(time),
        shared_boundary_sections)
    
    data = wrap_plate_boundaries(shared_boundary_sections,0.)
    print 'here'
    ret = json.dumps(pretty_floats(data))
   
    return HttpResponse(ret, content_type='application/json')


