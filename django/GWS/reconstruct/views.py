from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings


#from get_model import get_reconstruction_model_dict
from utils.get_model import get_reconstruction_model_dict
from utils.wrapping_tools import wrap_reconstructed_polygons

import sys, json

import pygplates
import numpy as np

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


def motion_path(request):

    seedpoints = request.GET.get('seedpoints', None)
    times = request.GET.get('timespec', '0,100,10')
    time = request.GET.get('time', 0)
    RelativePlate = request.GET.get('fixplate', 0)
    MovingPlate = request.GET.get('movplate', None)
    model = request.GET.get('model','SETON2012')

    points = []
    if seedpoints:
        ps = seedpoints.split(',')
        if len(ps)%2==0:
            for lat,lon in zip(ps[1::2], ps[0::2]):
                points.append((float(lat),float(lon)))

    seed_points_at_digitisation_time = pygplates.MultiPointOnSphere(points)

    if times:
        ts = times.split(',')
        if len(ts)==3:
            times = np.arange(float(ts[0]),float(ts[1])+0.1,float(ts[2]))

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (MODEL_STORE,model,model_dict['RotationFile'])))

    # Create the motion path feature
    digitisation_time = 0
    #seed_points_at_digitisation_time = pygplates.MultiPointOnSphere([SeedPoint])
    motion_path_feature = pygplates.Feature.create_motion_path(
            seed_points_at_digitisation_time,
            times = times,
            valid_time=(2000, 0),
            relative_plate=int(RelativePlate),
            reconstruction_plate_id = int(MovingPlate))

    # Create the shape of the motion path
    reconstruction_time = 0
    reconstructed_motion_paths = []
    pygplates.reconstruct(
            motion_path_feature, rotation_model, reconstructed_motion_paths, reconstruction_time,
            reconstruct_type=pygplates.ReconstructType.motion_path)

    #for reconstructed_motion_path in reconstructed_motion_paths:
    #    trail = reconstructed_motion_path.get_motion_path().to_lat_lon_array()

    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for reconstructed_motion_path in reconstructed_motion_paths:
        Dist = []
        for segment in reconstructed_motion_path.get_motion_path().get_segments():
            Dist.append(segment.get_arc_length()*pygplates.Earth.mean_radius_in_kms)
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        feature["geometry"]["type"] = "Polyline"
        #### NEED TO FLIP COORDINATES
        feature["geometry"]["coordinates"] = [reconstructed_motion_path.get_motion_path().to_lat_lon_list()]
        feature["geometry"]["distance"] = Dist
        data["features"].append(feature)

    ret = json.dumps(pretty_floats(data))
   
    return HttpResponse(ret, content_type='application/json')


def flowline(request):

    ret = json.dumps(pretty_floats(data))
   
    return HttpResponse(ret, content_type='application/json')



