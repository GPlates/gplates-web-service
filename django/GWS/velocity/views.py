from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings

import sys, json
import numpy as np

from utils.get_model import get_reconstruction_model_dict
from utils.velocity_tools import get_velocities
from utils.create_gpml import create_gpml_regular_long_lat_mesh,create_gpml_healpix_mesh

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
        return dict((k, pretty_floats(v)) for k, v in list(obj.items()))
    elif isinstance(obj, (list, tuple)):
        return list(map(pretty_floats, obj))             
    return obj


def velocity_within_topological_boundaries(request):
    """
    http GET request to retrieve plate velocities within topological plate polygons

    **usage**
    
    <http-address-to-gws>/velocity/plate_polygons/time=\ *reconstruction_time*\&model=\ *reconstruction_model*\&velocity_type=\ *velocity_type*\&domain_type=\ *domain_type*
    
    **parameters:**

    *time* : time for reconstruction [default=0]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    *velocity_type* : String specifying the type of velocity representation to return. Can be 'MagAzim' for 
                      magnitude/azimuth, or 'east_north' for velocity components in east and north directions 
                      [default='MagAzim']

    *domain_type* : String specifying the arrangement of domain points on which velocities are calculated. Can
                    be 'longLatGrid' for regular spacing in longitude/latitude, or 'healpix' for an equal area
                    distribution on the sphere [default='longLatGrid']

    **returns:**

    json containing velocity vector features
    """

    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)
    velocity_type = request.GET.get('velocity_type','MagAzim')
    domain_type = request.GET.get('domain_type','longLatGrid')

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

    topology_features= []
    pygplates.resolve_topologies([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,pp)) for pp in model_dict['PlatePolygons']], 
        rotation_model, topology_features, reconstruction_time=float(time))
    #print(topology_features)

    if domain_type=='longLatGrid':
        domain_features = create_gpml_regular_long_lat_mesh(1.,feature_type='MeshNode')
        lat,lon,vel1,vel2,plate_ids = get_velocities(rotation_model,topology_features,float(time),
                                                     velocity_domain_features=domain_features,
                                                     velocity_type=velocity_type, topology_flag=True)

    elif domain_type=='healpix':
        domain_features = create_gpml_healpix_mesh(32,feature_type='MeshNode')
        lat,lon,vel1,vel2,plate_ids = get_velocities(rotation_model,topology_features,float(time),
                                                     velocity_domain_features=domain_features,
                                                     velocity_type=velocity_type, topology_flag=True)
    
    # prepare the response to be returned
    ret='{"coordinates":['
    for p in zip(lat,lon,vel1,vel2,plate_ids):
        ret+='[{0:5.2f},{1:5.2f},{2:5.2f},{3:5.2f},{4:5.2f}],'.format(
            p[1],p[0],p[2],p[3],p[4])
    ret=ret[0:-1]
    ret+=']}'

    return HttpResponse(ret, content_type='application/json')


def velocity_within_static_polygons(request):
    """
    http GET request to retrieve plate velocities within static polygons

    **usage**
    
    <http-address-to-gws>/velocity/static_polygons/time=\ *reconstruction_time*\&model=\ *reconstruction_model*\&velocity_type=\ *velocity_type*\&domain_type=\ *domain_type*
    
    **parameters:**

    *time* : time for reconstruction [default=0]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    *velocity_type* : String specifying the type of velocity representation to return. Can be 'MagAzim' for 
                      magnitude/azimuth, or 'east_north' for velocity components in east and north directions 
                      [default='MagAzim']

    *domain_type* : String specifying the arrangement of domain points on which velocities are calculated. Can
                    be 'longLatGrid' for regular spacing in longitude/latitude, or 'healpix' for an equal area
                    distribution on the sphere [default='longLatGrid']

    **returns:**

    json containing velocity vector features
    """

    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)
    velocity_type = request.GET.get('velocity_type','MagAzim')
    domain_type = request.GET.get('domain_type','longLatGrid')

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

    static_polygons = pygplates.FeatureCollection(str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons'])))

    if domain_type=='longLatGrid':
        domain_features = create_gpml_regular_long_lat_mesh(1.,feature_type='MeshNode')
        lat,lon,vel1,vel2,plate_ids = get_velocities(rotation_model,static_polygons,float(time),
                                                     velocity_domain_features=domain_features,
                                                     velocity_type=velocity_type)

    elif domain_type=='healpix':
        domain_features = create_gpml_healpix_mesh(32,feature_type='MeshNode')
        lat,lon,vel1,vel2,plate_ids = get_velocities(rotation_model,static_polygons,float(time),
                                                     velocity_domain_features=domain_features,
                                                     velocity_type=velocity_type)
    
    # prepare the response to be returned
    ret='{"coordinates":['
    for p in zip(lat,lon,vel1,vel2,plate_ids):
        ret+='[{0:5.2f},{1:5.2f},{2:5.2f},{3:5.2f},{4:5.2f}],'.format(
            p[1],p[0],p[2],p[3],p[4])
    ret=ret[0:-1]
    ret+=']}'

    return HttpResponse(ret, content_type='application/json')
