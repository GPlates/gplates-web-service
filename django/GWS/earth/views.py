from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from StringIO import StringIO

# Create your views here.

import numpy as np
from utils.get_model import get_reconstruction_model_dict
from utils.create_gpml import create_gpml_crustal_thickness
from utils.sphere_tools import random_points_on_sphere,sampleOnSphere,healpix_mesh


def litho1(request):

    mode = request.GET.get('mode', 'random_points')
    filename = request.GET.get('filename', 'litho1_scalar_coverage.gpmlz')
    if mode=='healpix':
        Nstr = request.GET.get('N', 64)
    else:
        Nstr = request.GET.get('N', 100000)

    N = int(Nstr)

    data = np.loadtxt('%s/litho1.0_CrustThickness.csv' % settings.EARTH_STORE_DIR,delimiter=',')

    if mode=='healpix':
        longitude_array,latitude_array = healpix_mesh(N)
    else:
        longitude_array,latitude_array = random_points_on_sphere(N)

    d,l = sampleOnSphere(data[:,1],
                         data[:,0],
                         data[:,2], 
                         latitude_array, longitude_array,
                         n=4)
    
    interp_thickness = data[:,2].ravel()[l]

    create_gpml_crustal_thickness(longitude_array,
                                  latitude_array,
                                  interp_thickness,
                                  filename)
   
    f = StringIO(file(filename, "rb").read())

    response = HttpResponse(f, content_type = 'application/gpmlz')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    #response['Content-Length'] = filename.tell()

    return response


def paleolithology(request):

    anchor_plate_id = request.GET.get('pid', 0)
    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

    paleolithology_datafile = '%s/boucot_paleolithology_combined.shp' % settings.EARTH_STORE_DIR

    static_polygons_filename = str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons']))

    assigned_features = pygplates.partition_into_plates(
        static_polygons_filename,
        rotation_model,
        paleolithology_datafile,
        properties_to_copy = [
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period],
        partition_method = pygplates.PartitionMethod.most_overlapping_plate
    )

    reconstructed_paleolithology_points = []
    pygplates.reconstruct(
        assigned_features, 
        rotation_model, 
        reconstructed_paleolithology_points,
        float(time),
        anchor_plate_id=anchor_plate_id)

    coords=len(ids)*[[]]
    for g in reconstructed_paleolithology_points:
        coords[ids.index(g.get_feature().get_feature_id().get_string())]=(
            [g.get_reconstructed_geometry().to_lat_lon()[1],
            g.get_reconstructed_geometry().to_lat_lon()[0]])

    ret='{"type":"FeatureCollection","features":['
    for c,p in zip(coords,valid_periods):
        ret+='{"type":"Feature","geometry":'
        if c:
            print c
            ret+='{'+'"type":"Point","coordinates":[{0:5.2f},{1:5.2f}]'.format(c[0],c[1])+'},'
        else:
            ret+='null,'
        ret+='"properties":{'+'"valid_time":[{0},"{1}"]'.format(p[0],p[1])+'}},'

    ret=ret[0:-1]
    ret+=']}'

    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    
    #TODO: 
    #The "*" makes the service wide open to anyone. We should implement access control when time comes. 
    response['Access-Control-Allow-Origin'] = '*'
    return response

