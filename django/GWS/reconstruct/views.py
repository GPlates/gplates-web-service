from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect

#from get_model import get_reconstruction_model_dict
from utils.get_model import get_reconstruction_model_dict
from utils.wrapping_tools import wrap_reconstructed_polygons
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

    else:
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
    central_meridian = request.GET.get('central_meridian', 0)   
 
    model_dict = get_reconstruction_model_dict(model)
    model_string = str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['RotationFile']))

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

    reconstructed_polygons = []
    pygplates.reconstruct(
        str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['Coastlines'])), 
        rotation_model, 
        reconstructed_polygons,
        float(time),
        anchor_plate_id=anchor_plate_id)
  
    new_reconstructed_polygons=[] 
    for p in reconstructed_polygons:
        if p.get_reconstructed_geometry().get_orientation() == pygplates.PolygonOnSphere.Orientation.clockwise:
            new_reconstructed_polygons.append(p)
        else:
            print 'invalid p'
    data = wrap_reconstructed_polygons(new_reconstructed_polygons,0.)

    ret = json.dumps(pretty_floats(data))
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/ 
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
    
    data = wrap_reconstructed_polygons(reconstructed_polygons,0.)
    
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
    reconstruction_time = 0
    reconstructed_motion_paths = []
    pygplates.reconstruct(
            motion_path_feature, rotation_model, reconstructed_motion_paths, reconstruction_time,
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
    except:
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
        print feature["properties"]
        data["features"].append(feature)

    ret = json.dumps(pretty_floats(data))
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response


#put below code here temporarily.
#some of the coastline polygons have holes inside them.
#it must be addressed somehow.
import cProfile , pstats, ast, StringIO

#@request_access
def get_coastline_polygons_low(request):
    """
    http GET request to retrieve reconstructed low resolution coastlines polygons

    TEMPORARY IMPLEMENTATION
    """
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
    
    model_dict = get_reconstruction_model_dict(settings.MODEL_DEFAULT)
    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,settings.MODEL_DEFAULT,rot_file)) for rot_file in model_dict['RotationFile']])


    '''
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(20)
    print s.getvalue()
    '''
    '''
    pygplates.reconstruct(
        feature_collection,
        rotation_model,
        reconstructed_polygons,
        float(time))
    '''
    if True:
        print 'reconstruct file'
        anchor_plate_id = request.GET.get('pid', 0)
        time = request.GET.get('time', 0)
        model = request.GET.get('model',settings.MODEL_DEFAULT)
        
        model_dict = get_reconstruction_model_dict(model)
        model_string = str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['RotationFile']))

        rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
            (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

        reconstructed_polygons = []
        pygplates.reconstruct(
            str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['Coastlines'])), 
            rotation_model, 
            reconstructed_polygons,
            float(time),
            anchor_plate_id=anchor_plate_id)

 
    wrap=True
    
    polygons=[]
    central_meridian = 0
   
    if wrap:
        wrapped_polygons=[]
        date_line_wrapper = pygplates.DateLineWrapper(central_meridian)
        for p in reconstructed_polygons:
            wrapped_polygons += date_line_wrapper.wrap(p.get_reconstructed_geometry(),2.0)
        for p in wrapped_polygons:
            lats=[i.get_latitude() for i in p.get_exterior_points()]
            lons=[i.get_longitude() for i in p.get_exterior_points()]
            if pygplates.PolygonOnSphere(zip(lats+lats[:1],lons+lons[:1])).get_orientation() == pygplates.PolygonOnSphere.Orientation.clockwise:
                #pass
                polygons.append((lons,lats))
            else:
                polygons.append((lons[::-1],lats[::-1]))
    else:
        for p in reconstructed_polygons:
            lats, lons = zip( *p.get_reconstructed_geometry().to_lat_lon_list())
            polygons.append((list(lons),list(lats)))

    data = {"type": "FeatureCollection"}
    data["features"] = []
    for p in polygons:
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        feature["geometry"]["type"] = "Polygon"

        #make sure the coordinates are valid.
        lats=p[1]
        lons=p[0]
        #print lats, lons
        #some map plotting program(such as leaflet) does not like points on the map boundary,
        #for example the longitude 180 and -180.
        #So, move the points slightly inwards.
        for idx, x in enumerate(lons):
            if x<central_meridian-179.99:
                lons[idx] = central_meridian-179.99
            elif x>central_meridian+179.99:
                lons[idx] = central_meridian+179.99
        for idx, x in enumerate(lats):
            if x<-89.99:
                lats[idx] = -89.99
            elif x>89.99:
                lats[idx] = 89.99
        feature["geometry"]["coordinates"] = [zip(lons+lons[:1],lats+lats[:1])]

        data["features"].append(feature)
    ret = json.dumps(pretty_floats(data))
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response

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
