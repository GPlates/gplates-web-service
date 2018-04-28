from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect

#from get_model import get_reconstruction_model_dict
from utils.get_model import get_reconstruction_model_dict,is_time_valid_model
from utils.wrapping_tools import wrap_reconstructed_polygons,process_reconstructed_polygons
from utils.access_control import request_access

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


@csrf_exempt
def reconstruct_points(request):
    """
    http GET request to reconstruct points

    **usage**
    
    <http-address-to-gws>/reconstruct/reconstruct_points/points=\ *points*\&plate_id=\ *anchor_plate_id*\&time=\ *reconstruction_time*\&model=\ *reconstruction_model*
    
    **parameters:**

    *points* : list of points long,lat comma separated coordinates of points to be reconstructed [Required]

    *anchor_plate_id* : integer value for reconstruction anchor plate id [default=0]

    *time* : time for reconstruction [required]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    **returns:**

    json list of long,lat reconstructed coordinates
    """
    if request.method == 'POST':
        params = request.POST
    elif request.method == 'GET':
        params = request.GET
    else:
        return HttpResponseBadRequest('Unrecognized request type')

    points = params.get('points', None)
    anchor_plate_id = params.get('pid', 0)
    time = params.get('time', None)
    model = params.get('model',settings.MODEL_DEFAULT)
    if 'fc' in params:
        return_feature_collection = True
    else:
        return_feature_collection = False

    if 'return_null_points' in params:
        return_null_points = True
    else:
        return_null_points = False

    timef=0.0
    if not time:
        return HttpResponseBadRequest('The "time" parameter cannot be empty.')
    else:
        try:
            timef = float(time)
        except:
            return HttpResponseBadRequest('The "time" parameter is invalid ({0}).'.format(time))

    try:
        anchor_plate_id = int(anchor_plate_id)
    except:
        return HttpResponseBadRequest('The "pid" parameter is invalid ({0}).'.format(anchor_plate_id))

    model_dict = get_reconstruction_model_dict(model)

    if not model_dict:
        return HttpResponseBadRequest('The "model" ({0}) cannot be recognized.'.format(model))

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

    static_polygons_filename = str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons']))

    # create point features from input coordinates
    point_features = []
    if points:
        ps = points.split(',')
        if len(ps)%2==0:
            try:
                for lat,lon in zip(ps[1::2], ps[0::2]):
                    point_feature = pygplates.Feature()
                    point_feature.set_geometry(pygplates.PointOnSphere(float(lat),float(lon)))
                    point_features.append(point_feature)
            except pygplates.InvalidLatLonError as e:
                return HttpResponseBadRequest('Invalid longitude or latitude ({0}).'.format(e)) 
        else:
            return HttpResponseBadRequest('The longitude and latitude should come in pairs ({0}).'.format(points))
    else:
        return HttpResponseBadRequest('The "points" parameter is missing.')
 
    # assign plate-ids to points using static polygons
    assigned_point_features = pygplates.partition_into_plates(
        static_polygons_filename,
        rotation_model,
        point_features,
        properties_to_copy = [
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period])

    ids=[]
    valid_periods=[]
    for f in assigned_point_features:
        ids.append(f.get_feature_id().get_string())
        valid_periods.append(f.get_valid_time())

    # reconstruct the points
    assigned_point_feature_collection = pygplates.FeatureCollection(assigned_point_features)
    reconstructed_feature_geometries = []
    pygplates.reconstruct(assigned_point_feature_collection,
        rotation_model, 
        reconstructed_feature_geometries, 
        timef,
        anchor_plate_id=anchor_plate_id)

    coords=len(ids)*[[]]
    for g in reconstructed_feature_geometries:
        coords[ids.index(g.get_feature().get_feature_id().get_string())]=(
            [g.get_reconstructed_geometry().to_lat_lon()[1],
            g.get_reconstructed_geometry().to_lat_lon()[0]])

    # prepare the response to be returned
    if not return_feature_collection:
        ret='{"type":"MultiPoint","coordinates":['

        for c in coords:
            if c:
                ret+='[{0:5.2f},{1:5.2f}],'.format(c[0],c[1])
            elif return_null_points:
                ret+='null,'

    else:
        ret='{"type":"FeatureCollection","features":['
        for c,p in zip(coords,valid_periods):
            ret+='{"type":"Feature","geometry":'
            if c:
                print c
                ret+='{'+'"type":"Point","coordinates":[{0:5.2f},{1:5.2f}]'.format(c[0],c[1])+'},'
            else:
                ret+='null,'
            
            #write out begin and end time
            if p[0] == pygplates.GeoTimeInstant.create_distant_past():
                begin_time = '"distant past"'
            else:
                begin_time = p[0]
            if p[1] == pygplates.GeoTimeInstant.create_distant_future():
                end_time = '"distant future"'
            else:
                end_time=p[1]
            ret+='"properties":{'+'"valid_time":[{0},{1}]'.format(begin_time,end_time)+'}},'

    ret=ret[0:-1]
    ret+=']}'

    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    
    #TODO: 
    #The "*" makes the service wide open to anyone. We should implement access control when time comes. 
    response['Access-Control-Allow-Origin'] = '*'
    return response


def get_coastline_polygons(request):
    """
    http GET request to retrieve reconstructed coastline polygons

    **usage**
    
    <http-address-to-gws>/reconstruct/coastlines/plate_id=\ *anchor_plate_id*\&time=\ *reconstruction_time*\&model=\ *reconstruction_model*
    
    **parameters:**

    *anchor_plate_id* : integer value for reconstruction anchor plate id [default=0]

    *time* : time for reconstruction [required]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    **returns:**

    json containing reconstructed coastline features
    """

    anchor_plate_id = request.GET.get('pid', 0)
    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    wrap = True
    central_meridian = 0
    if 'central_meridian' in request.GET:
        try:
            central_meridian = float(request.GET['central_meridian'])   
            wrap = True
        except:
            print 'Invalid central meridian.'        

    avoid_map_boundary = False
    if 'avoid_map_boundary' in request.GET:
        avoid_map_boundary = True

    model_dict = get_reconstruction_model_dict(model)

    if not is_time_valid_model(model_dict,time):
        return HttpResponseBadRequest('Requested time %s not available for model %s' % (time,model))

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

    reconstructed_polygons = []
    pygplates.reconstruct(
        str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['Coastlines'])), 
        rotation_model, 
        reconstructed_polygons,
        float(time),
        anchor_plate_id=anchor_plate_id)

    data = process_reconstructed_polygons(reconstructed_polygons,
                                          wrap,
                                          central_meridian,
                                          avoid_map_boundary)

    ret = json.dumps(pretty_floats(data))
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response


def get_static_polygons(request):
    """
    http GET request to retrieve reconstructed static polygons

    **usage**
    
    <http-address-to-gws>/reconstruct/static_polygons/plate_id=\ *anchor_plate_id*\&time=\ *reconstruction_time*\&model=\ *reconstruction_model*
    
    **parameters:**

    *anchor_plate_id* : integer value for reconstruction anchor plate id [default=0]

    *time* : time for reconstruction [required]

    *model* : name for reconstruction model [defaults to default model from web service settings]

    **returns:**

    json containing reconstructed coastline features
    """

    anchor_plate_id = request.GET.get('pid', 0)
    time = request.GET.get('time', 0)
    model = request.GET.get('model',settings.MODEL_DEFAULT)

    wrap = True
    central_meridian = 0
    if 'central_meridian' in request.GET:
        try:
            central_meridian = float(request.GET['central_meridian'])   
            wrap = True
        except:
            print 'Invalid central meridian.'        

    avoid_map_boundary = False
    if 'avoid_map_boundary' in request.GET:
        avoid_map_boundary = True

    model_dict = get_reconstruction_model_dict(model)
    
    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

    reconstructed_polygons = []
    pygplates.reconstruct(
        str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons'])), 
        rotation_model, 
        reconstructed_polygons,
        float(time),
        anchor_plate_id=anchor_plate_id)
    
    data = process_reconstructed_polygons(reconstructed_polygons,
                                          wrap,
                                          central_meridian,
                                          avoid_map_boundary)
    
    ret = json.dumps(pretty_floats(data))

    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')

    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response


def motion_path(request):
    """
    http GET request to retrieve reconstructed static polygons

    **usage**
    
    <http-address-to-gws>/reconstruct/motion_path/seedpoints=\ *points*\&timespec=\ *time_list*\&fixplate=\ *fixed_plate_id*\&movplate=\ *moving_plate_id*\&time=\ *reconstruction_time*\&model=\ *reconstruction_model*
    
    :param seedpoints: integer value for reconstruction anchor plate id [required]

    :param timespec: specification for times for motion path construction, in format 'mintime,maxtime,increment' [defaults to '0,100,10']

    :param time: time for reconstruction [default=0]

    :param fixplate: integer plate id for fixed plate [default=0]

    :param movplate: integer plate id for moving plate [required]

    :param model: name for reconstruction model [defaults to default model from web service settings]

    :returns:  json containing reconstructed motion path features
    """
    seedpoints = request.GET.get('seedpoints', None)
    times = request.GET.get('timespec', '0,100,10')
    reconstruction_time = request.GET.get('time', 0)
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

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

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
    #reconstruction_time = 0
    reconstructed_motion_paths = []
    pygplates.reconstruct(
            motion_path_feature, rotation_model, reconstructed_motion_paths, float(reconstruction_time),
            reconstruct_type=pygplates.ReconstructType.motion_path)

    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for reconstructed_motion_path in reconstructed_motion_paths:
        Dist = []
        for segment in reconstructed_motion_path.get_motion_path().get_segments():
            Dist.append(segment.get_arc_length()*pygplates.Earth.mean_radius_in_kms)
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        feature["geometry"]["type"] = "Polyline"
        #### NOTE CODE TO FLIP COORDINATES TO 
        feature["geometry"]["coordinates"] = [[(lon,lat) for lat,lon in reconstructed_motion_path.get_motion_path().to_lat_lon_list()]]
        feature["geometry"]["distance"] = Dist
        data["features"].append(feature)

    ret = json.dumps(pretty_floats(data))
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response


def flowline(request):
    """
    http GET request to retrieve reconstructed static polygons
    
    NOT YET IMPLEMENTED
    """

    ret = json.dumps(pretty_floats(data))
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response


@csrf_exempt
def html_model_list(request):

    df = pd.read_csv('%s/%s' % (settings.PALEO_STORE_DIR,'ngeo2429-s2.csv'),index_col='Deposit number')
    html_table = df.to_html(index=False)
    return render(
        request,
        'list_template.html',
        {
            'html_table': html_table
        } 
    )


@csrf_exempt
def reconstruct_feature_collection(request):

    if request.method == 'POST':
        params = request.POST
    elif request.method == 'GET':
        params = request.GET
    else:
        return HttpResponseBadRequest('Unrecognized request type')

    anchor_plate_id = params.get('pid', 0)

    if 'time' in params:
        time = params['time']
    elif 'geologicage' in params:
        time = params['geologicage']
    else:
        time = 140 #default reconstruction age

    output_format = params.get('output', 'geojson')
    fc_str = params.get('feature_collection')
    model = str(params.get('model',settings.MODEL_DEFAULT))
    
    if 'keep_properties' in params:
        keep_properties = True
    else:
        keep_properties = False

    try:
        timef = float(time)
    except:
        return HttpResponseBadRequest('The "time" parameter is invalid ({0}).'.format(time))

    try:
        anchor_plate_id = int(anchor_plate_id)
    except:
        return HttpResponseBadRequest('The "pid" parameter is invalid ({0}).'.format(anchor_plate_id))
 
    # Convert geojson input to gplates feature collection
    features=[]
    try:
        fc = json.loads(fc_str)#load the input feature collection
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
            
            if keep_properties and 'properties' in f:
                for pk in f['properties']:           
                    p = f['properties'][pk] 
                    if isinstance(p, unicode):
                        p=str(p) 
                    feature.set_shapefile_attribute(str(pk),p)
            
            features.append(feature)
    except Exception as e:
        #print e
        return HttpResponseBadRequest('Invalid input feature collection')

    model_dict = get_reconstruction_model_dict(model)
    if not model_dict:
        return HttpResponseBadRequest('The "model" ({0}) cannot be recognized.'.format(model))

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

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
    pygplates.reconstruct(assigned_features, 
        rotation_model, 
        reconstructed_geometries, 
        timef, 
        anchor_plate_id=anchor_plate_id)

    # convert feature collection back to geojson
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
            return HttpResponseServerError('Unsupported Geometry Type.')

        feature["properties"] = {}
        if keep_properties:
            for pk in g.get_feature().get_shapefile_attributes():
                feature["properties"][pk] = g.get_feature().get_shapefile_attribute(pk)
        #print feature["properties"]
        data["features"].append(feature)

    ret = json.dumps(pretty_floats(data))
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response


#@request_access
def get_coastline_polygons_low(request):
    return get_coastline_polygons(request)

#negative -- counter-clockwise
#positive -- clockwise
def check_polygon_orientation(lons, lats):
    lats = lats+lats[:1]
    lons = lons+lons[:1]
    length = len(lats)
    last_lon=lons[0]
    last_lat=lats[0]
    result=0
    for i in range(1,length):
        result+=(lons[i]-last_lon)*(lats[i]+last_lat)
        last_lon=lons[i]
        last_lat=lats[i]
    return result
