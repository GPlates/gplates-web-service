from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings


#from get_model import get_reconstruction_model_dict
from utils.get_model import get_reconstruction_model_dict
from utils.wrapping_tools import wrap_reconstructed_polygons

import sys, json

import pygplates
import numpy as np


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
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,model_dict['RotationFile'])))
    static_polygons_filename = str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons']))

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
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    
    #TODO: 
    response['Access-Control-Allow-Origin'] = 'portal.gplates.org'
    #response['Access-Control-Allow-Origin'] = '*'
    return response


def get_coastline_polygons(request):
    
    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)
    
    model_dict = get_reconstruction_model_dict(model)
    model_string = str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['RotationFile']))

    rotation_model = pygplates.RotationModel(str('%s/%s/%s' % 
        (settings.MODEL_STORE_DIR,model,model_dict['RotationFile'])))

    reconstructed_polygons = []
    pygplates.reconstruct(
        str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['Coastlines'])), 
        rotation_model, 
        reconstructed_polygons,
        float(time))
    
    data = wrap_reconstructed_polygons(reconstructed_polygons,0.)

    ret = json.dumps(pretty_floats(data))
  
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/ 
    response = HttpResponse(ret, content_type='application/json')
    
    #TODO:
    response['Access-Control-Allow-Origin'] = 'portal.gplates.org'
    #response['Access-Control-Allow-Origin'] = '*'
    return response

def get_static_polygons(request):

    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)
    
    rotation_model = pygplates.RotationModel(str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,model_dict['RotationFile'])))    

    reconstructed_polygons = []
    pygplates.reconstruct(
        str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons'])), 
        rotation_model, 
        reconstructed_polygons,
        float(time))
    
    data = wrap_reconstructed_polygons(reconstructed_polygons,0.)
    
    ret = json.dumps(pretty_floats(data))

    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')

    #TODO:
    response['Access-Control-Allow-Origin'] = 'portal.gplates.org'
    #response['Access-Control-Allow-Origin'] = '*'
    return response



def motion_path(request):

    seedpoints = request.GET.get('seedpoints', None)
    times = request.GET.get('timespec', '0,100,10')
    time = request.GET.get('time', 0)
    RelativePlate = request.GET.get('fixplate', 0)
    MovingPlate = request.GET.get('movplate', None)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

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
        (settings.MODEL_STORE_DIR,model,model_dict['RotationFile'])))

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
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = 'portal.gplates.org'
    #response['Access-Control-Allow-Origin'] = '*'
    return response


def flowline(request):

    ret = json.dumps(pretty_floats(data))
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = 'portal.gplates.org'
    #response['Access-Control-Allow-Origin'] = '*'
    return response


def reconstruct_feature_collection(request):
    if request.method == 'POST':
        return HttpResponse('POST method is not accepted for now.')

    geologicage = request.GET.get('geologicage', 140)
    output_format = request.GET.get('output', 'geojson')
    fc_str = request.GET.get('feature_collection')
    fc = json.loads(fc_str)

    features=[]
    for f in fc['features']:
        geom = f['geometry']
        feature = pygplates.Feature()
        if geom['type'] == 'Point':
            feature.set_geometry(pygplates.PointOnSphere(
                float(geom['coordinates'][1]),
                float(geom['coordinates'][0])))
        if geom['type'] == 'LineString':
            feature.set_geometry(
                pygplates.PolylineOnSphere([(point[1],point[0]) for point in geom['coordinates']]))
        if geom['type'] == 'Polygon':
            feature.set_geometry(
                pygplates.PolygonOnSphere([(point[1],point[0]) for point in geom['coordinates'][0]]))
        if geom['type'] == 'MultiPoint':
             feature.set_geometry(
                pygplates.MultiPointOnSphere([(point[1],point[0]) for point in geom['coordinates']]))

        features.append(feature)


    model = request.GET.get('model',settings.MODEL_DEFAULT)
    model_dict = get_reconstruction_model_dict(model)
    rotation_model = pygplates.RotationModel(settings.MODEL_STORE_DIR+model+'/'+model_dict['RotationFile'])

    assigned_features = pygplates.partition_into_plates(
        settings.MODEL_STORE_DIR+model+'/'+model_dict['StaticPolygons'],
        rotation_model,
        features,
        properties_to_copy = [
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period],

        partition_method = pygplates.PartitionMethod.most_overlapping_plate
    )

    reconstructed_geometries = []
    pygplates.reconstruct(assigned_features, rotation_model, reconstructed_geometries, float(geologicage), 0)


    data = {"type": "FeatureCollection"}
    data["features"] = []
    for g in reconstructed_geometries:
        geom =  g.get_reconstructed_geometry()
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        if isinstance(geom, pygplates.PointOnSphere):
            feature["geometry"]["type"] = "Point"
            p = geom.to_lat_lon_list()[0]
            feature["geometry"]["coordinates"] = [p[1], p[0]]
        elif isinstance(geom, pygplates.MultiPointOnSphere):
            feature["geometry"]["type"] = 'MultiPoint'
            feature["geometry"]["coordinates"] = [[lon,lat] for lat, lon in geom.to_lat_lon_list()]
        elif isinstance(geom, pygplates.PolylineOnSphere):
            feature["geometry"]["type"] = 'LineString'
            feature["geometry"]["coordinates"] = [[lon,lat] for lat, lon in geom.to_lat_lon_list()]
        elif isinstance(geom, pygplates.PolygonOnSphere):
            feature["geometry"]["type"] = 'Polygon'
            feature["geometry"]["coordinates"] = [[[lon,lat] for lat, lon in geom.to_lat_lon_list()]]
        else:
            raise 'Unrecognized Geometry Type.'

        feature["properties"]={}

        data["features"].append(feature)

    ret = json.dumps(pretty_floats(data))
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = 'portal.gplates.org'
    #response['Access-Control-Allow-Origin'] = '*'
    return response


#put below code here temporarily.
#some of the coastline polygons have holes inside them.
#it must be addressed somehow.
import cProfile , pstats, ast, StringIO

def get_coastline_polygons_low(request):
    #pr = cProfile.Profile()
    #pr.enable()

    time = request.GET.get('time', 0)
    features = []
    '''
    polygons = CoastlinePolygons.objects.all()
    #polygons = StaticPolygons.objects.all()

    for p in polygons:
        polygon_feature = pygplates.Feature()
        polygon_feature.set_geometry(
            pygplates.PolygonOnSphere([(lat,lon) for lon, lat in p.geom[0][0]]))
        polygon_feature.set_reconstruction_plate_id(int(p.plateid1))
        features.append(polygon_feature)
    '''
    shp_path = settings.MODEL_STORE_DIR+'/'+settings.MODEL_DEFAULT+'/coastlines_low_res/Seton_etal_ESR2012_Coastlines_2012.shp'

    model_dict = get_reconstruction_model_dict(settings.MODEL_DEFAULT)
    rotation_file_path = settings.MODEL_STORE_DIR+'/'+settings.MODEL_DEFAULT+"/"+model_dict['RotationFile']

    import shapefile
    sf = shapefile.Reader(shp_path)
    for record in sf.shapeRecords():
        if record.shape.shapeType != 5:
            continue
        for idx in range(len(record.shape.parts)):
            start_idx = record.shape.parts[idx]
            end_idx = len(record.shape.points)
            if idx < (len(record.shape.parts) -1):
                end_idx = record.shape.parts[idx+1]
            polygon_feature = pygplates.Feature()
            points = record.shape.points[start_idx:end_idx]
            polygon_feature.set_geometry(
                pygplates.PolygonOnSphere([(lat,lon) for lon, lat in points]))
            polygon_feature.set_reconstruction_plate_id(int(record.record[0]))
            features.append(polygon_feature)
            break

    feature_collection = pygplates.FeatureCollection(features)
    reconstructed_polygons = []
    rotation_model = pygplates.RotationModel(rotation_file_path)

    '''
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(20)
    print s.getvalue()
    '''
    pygplates.reconstruct(
        feature_collection,
        rotation_model,
        reconstructed_polygons,
        float(time))

    #return HttpResponse('OK')
    data = {"type": "FeatureCollection"}
    data["features"] = []
    for p in reconstructed_polygons:
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        feature["geometry"]["type"] = "Polygon"

        #make sure the coordinates are valid.
        lats, lons = zip( *p.get_reconstructed_geometry().to_lat_lon_list())
        lats = list(lats)
        lons = list(lons)
        #print lats, lons
        for idx, x in enumerate(lats):
            if x<-89.99:
                lats[idx] = -89.99
            if x>89.99:
                lats[idx] = 89.99

        for idx, x in enumerate(lons):
            if x<-179.99:
                lons[idx] = -179.99
            if x>179.99:
                lons[idx] = 179.99

        feature["geometry"]["coordinates"] = [zip(lons,lats)]

        data["features"].append(feature)
    ret = json.dumps(pretty_floats(data))

    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = 'portal.gplates.org'
    return response

