from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings

import sys, json

from get_model import get_reconstruction_model_dict

import pygplates

MODEL_DEFAULT = 'SETON2012'

MODEL_STORE = '/Users/Simon/GIT/gplates-web/MODELS/'


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
    model = request.GET.get('model','SETON2012')

    model_dict = get_reconstruction_model_dict(model)    

    features = []
    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (MODEL_STORE,model,model_dict['RotationFile'])))  

    resolved_polygons = []
    pygplates.resolve_topologies(
        str('%s/%s/%s' % (MODEL_STORE,model,model_dict['PlatePolygons'])),
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
        (MODEL_STORE,model,model_dict['RotationFile'])))   

    resolved_polygons = []
    shared_boundary_sections = []
    pygplates.resolve_topologies(
        str('%s/%s/%s' % (MODEL_STORE,model,model_dict['PlatePolygons'])),
        rotation_model, 
        resolved_polygons,
        float(time),
        shared_boundary_sections)
    
    data = wrap_plate_boundaries(shared_boundary_sections,0.)
    print 'here'
    ret = json.dumps(pretty_floats(data))
   
    return HttpResponse(ret, content_type='application/json')


#################################################################
def wrap_plate_boundaries(shared_boundary_sections,lon0=0,tesselate_degrees=1):
    
    wrapper = pygplates.DateLineWrapper(lon0)
    
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for shared_boundary_section in shared_boundary_sections:
        for shared_sub_segment in shared_boundary_section.get_shared_sub_segments():

            split_geometry = wrapper.wrap(shared_sub_segment.get_geometry(),tesselate_degrees)
            for geometry in split_geometry:
                feature = {"type": "Feature"}
                feature["geometry"] = {}
                feature["geometry"]["type"] = "Polyline"
                point_list = []
                for point in geometry.get_points():
                    point_list.append((point.to_lat_lon()[1],point.to_lat_lon()[0]))
                feature["geometry"]["coordinates"] = [point_list]
                feature["geometry"]["feature_type"] = str(shared_sub_segment.get_feature().get_feature_type())
                data["features"].append(feature)
    
    return data

def wrap_polygons(polygons,lon0=0,tesselate_degrees=1):
    
    wrapper = pygplates.DateLineWrapper(lon0)
    
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for polygon in polygons:
        split_geometry = wrapper.wrap(polygon.get_geometry(),tesselate_degrees)
        for geometry in split_geometry:
            feature = {"type": "Feature"}
            feature["geometry"] = {}
            feature["geometry"]["type"] = "Polygon"
            point_list = []
            for point in geometry.get_exterior_points():
                point_list.append((point.to_lat_lon()[1],point.to_lat_lon()[0]))
            feature["geometry"]["coordinates"] = [point_list]
            data["features"].append(feature)
    
    return data
