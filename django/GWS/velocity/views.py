from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings

import sys, json
import numpy as np

from utils.get_model import get_reconstruction_model_dict
from utils.velocity_tools import get_velocities

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


def velocity_within_topological_boundaries(request):
    
    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,model_dict['RotationFile'])))  

    topology_features = pygplates.FeatureCollection(str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,model_dict['PlatePolygons'])))

    lat,lon,vel_mag,vel_az = get_velocities(rotation_model,topology_features,float(time))
    
    # prepare the response to be returned
    ret='{"coordinates":['
    for p in zip(lat,lon,vel_mag,vel_az):
        ret+='[{0:5.2f},{1:5.2f},{2:5.2f},{3:5.2f}],'.format(
            p[1],p[0],p[2],p[3])
    ret=ret[0:-1]
    ret+=']}'

    return HttpResponse(ret, content_type='application/json')


def velocity_within_static_polygons(request):

    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,model_dict['RotationFile'])))  

    static_polygons = pygplates.FeatureCollection(str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons'])))

    lat,lon,vel_mag,vel_az = get_velocities(rotation_model,static_polygons,float(time))
    
    # prepare the response to be returned
    ret='{"coordinates":['
    for p1,p2,p3,p4 in zip(lat,lon,vel_mag,vel_az):
        ret+='[{0:5.2f},{1:5.2f},{2:5.2f},{3:5.2f}],'.format(
            p2,p1,p3,p4)
    ret=ret[0:-1]
    ret+=']}'

    return HttpResponse(ret, content_type='application/json')
