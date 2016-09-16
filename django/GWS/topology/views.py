from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings

import sys, json

from utils.get_model import get_reconstruction_model_dict
from utils.wrapping_tools import wrap_polygons, wrap_plate_boundaries

import pygplates


def index(request):
    return render_to_response(
        'list.html',
        context_instance = RequestContext(request,
            {}))

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
    
    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)    

    features = []
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
    
    time = request.GET.get('time', 0)
    model = request.GET.get('model','SETON2012')

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

