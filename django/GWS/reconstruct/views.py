from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings
import csv
import pandas as pd
from get_model import get_reconstruction_model_dict

import sys, json

import pygplates

MODEL_DEFAULT = 'SETON2012'

MODEL_STORE = '/Users/Simon/GIT/gplates-web/MODELS/'



def index(request):
    return render_to_response(
        'list.html',
        context_instance = RequestContext(request,
            {}))

def upload(request):
    file = request.FILES['paleodata']
    tmp = []
    for chunk in file.chunks():
        tmp.append(chunk)

    df = pd.DataFrame(tmp)
    print df

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mydata.csv"'
    writer = csv.writer(response)
    df.to_csv(response)

    return response
    #return  HttpResponse("OK")

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

def reconstruct_points(request):
    points = request.GET.get('points', None)
    plate_id = request.GET.get('pid', None)
    time = request.GET.get('time', None)
    model = request.GET.get('model',MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (MODEL_STORE,model,model_dict['RotationFile'])))
    static_polygons_filename = str('%s/%s/%s' % (MODEL_STORE,model,model_dict['StaticPolygons']))

    # create point features from input coordinates
    point_features = []
    if points:
        ps = points.split(',')
        if len(ps)%2==0:
            for lat,lon in zip(ps[1::2], ps[0::2]):
                point_feature = pygplates.Feature()
                point_feature.set_geometry(pygplates.PointOnSphere(float(lat),float(lon)))
                point_features.append(point_feature)
    
    # assign plate-ids to points using static polygons
    assigned_point_features = pygplates.partition_into_plates(
        static_polygons_filename,
        rotation_model,
        point_features,
        properties_to_copy = [
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period])

    # reconstruct the points
    assigned_point_feature_collection = pygplates.FeatureCollection(assigned_point_features)
    reconstructed_feature_geometries = []
    pygplates.reconstruct(assigned_point_feature_collection, rotation_model, reconstructed_feature_geometries, float(time))
    
    # prepare the response to be returned
    ret='{"coordinates":['
    for g in reconstructed_feature_geometries:
        ret+='[{0:5.2f},{1:5.2f}],'.format(
            g.get_reconstructed_geometry().to_lat_lon()[1],
            g.get_reconstructed_geometry().to_lat_lon()[0])
    ret=ret[0:-1]
    ret+=']}'
    return HttpResponse(ret, content_type='application/json')


def get_coastline_polygons(request):
    
    time = request.GET.get('time', 0)
    model = request.GET.get('model','SETON2012')
    
    model_dict = get_reconstruction_model_dict(model)
    model_string = str('%s/%s/%s' % (MODEL_STORE,model,model_dict['RotationFile']))

    rotation_model = pygplates.RotationModel(str('%s/%s/%s' % 
        (MODEL_STORE,model,model_dict['RotationFile'])))

    reconstructed_polygons = []
    pygplates.reconstruct(
        str('%s/%s/%s' % (MODEL_STORE,model,model_dict['Coastlines'])), 
        rotation_model, 
        reconstructed_polygons,
        float(time))
    
    data = wrap_reconstructed_polygons(reconstructed_polygons,0.)

    ret = json.dumps(pretty_floats(data))
   
    return HttpResponse(ret, content_type='application/json')


def get_static_polygons(request):
    
    time = request.GET.get('time', 0)
    model = request.GET.get('model','SETON2012')

    model_dict = get_reconstruction_model_dict(model)
    
    features = []
    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (MODEL_STORE,model,model_dict['RotationFile'])))    

    reconstructed_polygons = []
    pygplates.reconstruct(
        str('%s/%s/%s' % (MODEL_STORE,model,model_dict['StaticPolygons'])), 
        rotation_model, 
        reconstructed_polygons,
        float(time))
    
    data = wrap_reconstructed_polygons(reconstructed_polygons,0.)
    
    ret = json.dumps(pretty_floats(data))
   
    return HttpResponse(ret, content_type='application/json')



#################################################################
def wrap_reconstructed_polygons(reconstructed_polygons,lon0=0,tesselate_degrees=1):
    
    wrapper = pygplates.DateLineWrapper(lon0)
    
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for reconstructed_polygon in reconstructed_polygons:
        split_geometry = wrapper.wrap(reconstructed_polygon.get_reconstructed_geometry(),tesselate_degrees)
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

