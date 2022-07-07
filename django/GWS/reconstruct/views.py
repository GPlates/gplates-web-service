from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, \
HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect

#from get_model import get_reconstruction_model_dict
from utils.get_model import get_reconstruction_model_dict,is_time_valid_model
from utils.wrapping_tools import wrap_reconstructed_polygons,process_reconstructed_polygons
from utils.access_control import request_access
from utils.round_float import round_floats

import os, sys, json, traceback
import zipfile, io

import pygplates
import numpy as np

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
    pids_str = params.get('pids', None)
    #print(pids_str)
    pid_str = params.get('pid', None)

    return_null_points = True if 'return_null_points' in params else False
    return_feature_collection = True if 'fc' in params else False
    is_reverse = True if 'reverse' in params else False

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
        return HttpResponseBadRequest('The "anchor_plate_id" parameter is invalid ({0}).'.format(anchor_plate_id))

    model_dict = get_reconstruction_model_dict(model)

    if not model_dict:
        return HttpResponseBadRequest('The "model" ({0}) cannot be recognized.'.format(model))

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

    static_polygons_filename = str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons']))

    # create point features from input coordinates
    p_index=0
    point_features = []
    if points:
        ps = points.split(',')
        ps_len = len(ps)
        if ps_len%2==0:
            try:
                if pids_str:
                    pids=pids_str.split(',')
                    if len(pids) != ps_len//2:
                        return HttpResponseBadRequest('The number of plate ids must be the same with the number of points.')
                else:
                    if pid_str:
                        pids=(ps_len//2)*[int(pid_str)]
                    else:
                        pids=(ps_len//2)*[None]

                for lat,lon, pid_ in zip(ps[1::2], ps[0::2], pids):
                    point_feature = pygplates.Feature()
                    point_feature.set_geometry(pygplates.PointOnSphere(float(lat),float(lon)))
                    point_feature.set_name(str(p_index))
                    if pid_:
                        point_feature.set_reconstruction_plate_id(int(pid_))
                    point_features.append(point_feature)
                    p_index += 1
            except pygplates.InvalidLatLonError as e:
                return HttpResponseBadRequest('Invalid longitude or latitude ({0}).'.format(e)) 
            except ValueError as e:
                return HttpResponseBadRequest('Invalid value ({0}).'.format(e)) 
        else:
            return HttpResponseBadRequest('The longitude and latitude should come in pairs ({0}).'.format(points))
    else:
        return HttpResponseBadRequest('The "points" parameter is missing.')
 
    # assign plate-ids to points using static polygons
    partition_time = timef if is_reverse else 0.

    if not pids_str and not pid_str: #if user has provided plate id(s), do not partition(slow)
        #from time import time
        #start = time()

        #LOOK HERE !!!!
        #it seems when the partition_time is not 0
        #the returned assigned_point_features contains reverse reconstructed present-day geometries.
        #so, when doing reverse reconstruct, do not reverse reconstruct again later.  
        assigned_point_features = pygplates.partition_into_plates(
            static_polygons_filename,
            rotation_model,
            point_features,
            properties_to_copy = [
                pygplates.PartitionProperty.reconstruction_plate_id,
                pygplates.PartitionProperty.valid_time_period],
            reconstruction_time = partition_time
            )
        
        #end=time()
        #print(f'It took {end - start} seconds!')
    else:
        assigned_point_features = point_features

    # reconstruct the points
    assigned_point_feature_collection = pygplates.FeatureCollection(assigned_point_features)
    reconstructed_feature_geometries = []
    if not is_reverse:
        pygplates.reconstruct(
            assigned_point_feature_collection,
            rotation_model, 
            reconstructed_feature_geometries, 
            timef,
            anchor_plate_id=anchor_plate_id)  

    rfgs = p_index*[None]
    for rfg in reconstructed_feature_geometries:
        rfgs[int(rfg.get_feature().get_name())] = rfg
    
    assigned_fc = p_index*[None]
    for f in assigned_point_feature_collection:
        assigned_fc[int(f.get_name())] = f
    
    # prepare the response to be returned
    if not return_feature_collection:
        ret='{"type":"MultiPoint","coordinates":['
        for idx in range(p_index):
            lon = None
            lat = None
            if not is_reverse and rfgs[idx]:
                lon = rfgs[idx].get_reconstructed_geometry().to_lat_lon()[1]
                lat = rfgs[idx].get_reconstructed_geometry().to_lat_lon()[0]
            elif is_reverse and assigned_fc[idx]:
                lon = assigned_fc[idx].get_geometry().to_lat_lon()[1]
                lat = assigned_fc[idx].get_geometry().to_lat_lon()[0]

            if lon is not None and lat is not None:
                ret+='[{0:5.2f},{1:5.2f}],'.format(lon, lat)
            elif return_null_points:
                ret+='null,' #return null for invalid coordinates
            else:
                ret+='[{0:5.2f},{1:5.2f}],'.format(999.99, 999.99) #use 999.99 to indicate invalid coordinates

    else:
        ret='{"type":"FeatureCollection","features":['
        for idx in range(p_index):
            lon = None
            lat = None
            begin_time = None
            end_time = None
            if not is_reverse and rfgs[idx]:
                lon = rfgs[idx].get_reconstructed_geometry().to_lat_lon()[1]
                lat = rfgs[idx].get_reconstructed_geometry().to_lat_lon()[0]
            elif is_reverse and assigned_fc[idx]:
                lon = assigned_fc[idx].get_geometry().to_lat_lon()[1]
                lat = assigned_fc[idx].get_geometry().to_lat_lon()[0]

            if assigned_fc[idx]:
                valid_time = assigned_fc[idx].get_valid_time(None)
                if valid_time:
                    begin_time, end_time = valid_time

            ret+='{"type":"Feature","geometry":'
            if lon is not None and lat is not None:
                ret+='{'+'"type":"Point","coordinates":[{0:5.2f},{1:5.2f}]'.format(lon, lat)+'},'
            else:
                ret+='null,'
            if begin_time is not None and end_time is not None:
                #write out begin and end time
                if begin_time == pygplates.GeoTimeInstant.create_distant_past():
                    begin_time = '"distant past"'
                if end_time == pygplates.GeoTimeInstant.create_distant_future():
                    end_time = '"distant future"'
                ret+='"properties":{'+'"valid_time":[{0},{1}]'.format(begin_time,end_time)+'}},'
            else:
                ret+='"properties":{}'+'},'
            
    ret=ret[0:-1]
    ret+=']}'

    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    
    #TODO: 
    #The "*" makes the service wide open to anyone. We should implement access control when time comes. 
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

    json containing reconstructed static polygons features
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
            print('Invalid central meridian.')        

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
    
    ret = json.dumps(round_floats(data))

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
        feature["geometry"]["type"] = "LineString"
        #### NOTE CODE TO FLIP COORDINATES TO 
        feature["geometry"]["coordinates"] = [(lon,lat) for lat,lon in reconstructed_motion_path.get_motion_path().to_lat_lon_list()]
        feature["geometry"]["distance"] = Dist
        feature["properties"] = {}
        data["features"].append(feature)

    ret = json.dumps(round_floats(data))
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response


def flowline(request):
    """
    http GET request to retrieve reconstructed flowline
    
    NOT YET IMPLEMENTED
    """

    ret = json.dumps(round_floats(data))
    
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
                    if isinstance(p, str):
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

    ret = json.dumps(round_floats(data))
    
    #add header for CORS
    #http://www.html5rocks.com/en/tutorials/cors/
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response

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
#
#
#
@csrf_exempt
def reconstruct_files(request):
    if not request.method == "POST":
        return HttpResponseBadRequest('expecting post requests!')
    try:
        print((request.FILES))
        if not len(list(request.FILES.items())):
            return HttpResponseBadRequest("No File Received")

        if not os.path.isdir(settings.MEDIA_ROOT + "/rftmp"):
            os.makedirs(settings.MEDIA_ROOT + "/rftmp" )

        reconstructable_files = []
        
        for fs in request.FILES.lists():
            for f in fs[1]:
                print((f.name))
                (name,ext) = os.path.splitext(f.name)
                if ext in ['.shp', '.gpml','.gpmlz']:
                    reconstructable_files.append(f.name)
                with open(settings.MEDIA_ROOT + "/rftmp/" + f.name, 'wb+') as fp:
                    for chunk in f.chunks():
                        fp.write(chunk)

        time = request.POST.get('time', None)
        model = request.POST.get('model',settings.MODEL_DEFAULT)
        print(model)

        model_dict = get_reconstruction_model_dict(model)

        if not model_dict:
            return HttpResponseBadRequest('The "model" ({0}) cannot be recognized.'.format(model))
        
        rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
            (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

        static_polygons_filename = str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['StaticPolygons']))

        for f in reconstructable_files:
            #print(f)
            features = pygplates.partition_into_plates(
                static_polygons_filename,        
                rotation_model,
                (settings.MEDIA_ROOT + "/rftmp/" + f).encode("utf-8"),
                partition_method = pygplates.PartitionMethod.most_overlapping_plate,
                properties_to_copy = [pygplates.PartitionProperty.reconstruction_plate_id, 
                                      pygplates.PartitionProperty.valid_time_period]
            )

            feature_collection = pygplates.FeatureCollection(features)
            feature_collection.write((settings.MEDIA_ROOT + "/rftmp/" + f+'.partitioned.gpml').encode("utf-8"))

            if not os.path.isdir(settings.MEDIA_ROOT + "/rftmp/dst/"):
                os.makedirs(settings.MEDIA_ROOT + "/rftmp/dst/" )

            pygplates.reconstruct((settings.MEDIA_ROOT + "/rftmp/" + f+'.partitioned.gpml').encode("utf-8"), 
                                  rotation_model, 
                                  ((settings.MEDIA_ROOT + "/rftmp/dst/" + f + '_' + model + '_' + str(time) + 'Ma').replace('.','_') + '.shp').encode("utf-8"), 
                                  float(time))

        s = io.StringIO()
        zf = zipfile.ZipFile(s, "w")

        #settings.MEDIA_ROOT + '/rftmp/dst/reconstructed_files.zip', 'w', zipfile.ZIP_DEFLATED)
        for r, d, files in os.walk(settings.MEDIA_ROOT + "/rftmp/dst/"):
            if not files:
                return HttpResponseServerError('No output files have been created!') 
            for f in files:
                zf.write(os.path.join(r, f), 'reconstructed_files/'+f)
        zf.close()
        #f = StringIO(file(settings.MEDIA_ROOT + '/rftmp/dst/reconstructed_files.zip', "rb").read())

        response = HttpResponse(s.getvalue(), content_type = 'application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=reconstructed_files.zip'
        
        #clear_folder(settings.MEDIA_ROOT + "/rftmp" )
        #clear_folder(settings.MEDIA_ROOT + "/rftmp/dst")
        return response
    except:
        clear_folder(settings.MEDIA_ROOT + "/rftmp" )
        clear_folder(settings.MEDIA_ROOT + "/rftmp/dst")
        traceback.print_stack()
        traceback.print_exc(file=sys.stdout)
        err = traceback.format_exc()
        return HttpResponseBadRequest(err)

def clear_folder(path):
    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
