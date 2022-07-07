from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings

from utils.get_model import get_reconstruction_model_dict,is_time_valid_model
from utils.wrapping_tools import process_reconstructed_polygons
from utils.round_float import round_floats

import json, io
import pygplates
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
import cartopy.crs as ccrs
from shapely.geometry.polygon import Polygon

#@request_access
def get_coastline_polygons_low(request):
    return get_coastline_polygons(request)

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
    return_format = request.GET.get('fmt', '')
    edgecolor = request.GET.get('edgecolor', 'black')
    facecolor = request.GET.get('facecolor', 'none') 
    alpha = request.GET.get('alpha', 0.5)

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

    if not is_time_valid_model(model_dict,time):
        return HttpResponseBadRequest('Requested time %s not available for model %s' % (time,model))

    rotation_model = pygplates.RotationModel([str('%s/%s/%s' %
        (settings.MODEL_STORE_DIR,model,rot_file)) for rot_file in model_dict['RotationFile']])

    # reconstruct the coastlines
    reconstructed_polygons = []
    pygplates.reconstruct(
        str('%s/%s/%s' % (settings.MODEL_STORE_DIR,model,model_dict['Coastlines'])), 
        rotation_model, 
        reconstructed_polygons,
        float(time),
        anchor_plate_id=anchor_plate_id)
    
    #wrap=False #for debug

    # plot and return the map
    if return_format=='png':
        if wrap:
            date_line_wrapper = pygplates.DateLineWrapper(central_meridian)
        else:
            date_line_wrapper = None
        return get_map(reconstructed_polygons, edgecolor, facecolor, alpha, date_line_wrapper) 

    data = process_reconstructed_polygons(reconstructed_polygons,
                                          wrap,
                                          central_meridian,
                                          avoid_map_boundary)

    ret = json.dumps(round_floats(data))
    
    response = HttpResponse(ret, content_type='application/json')
    #TODO:
    response['Access-Control-Allow-Origin'] = '*'
    return response

#
#
#
def get_map(reconstructed_polygons, edgecolor, facecolor, alpha, date_line_wrapper):
    try:
        fig = plt.figure(figsize=(12,8),dpi=300)
        ax = plt.axes(projection=ccrs.PlateCarree())
        #ax.gridlines()
        #ax.set_extent([-100, 30, 0, 20])
        ax.set_global()
        ax.background_patch.set_visible(False)   # Background
        ax.outline_patch.set_visible(False)      # Borders
        imgdata = io.BytesIO()
        
        # wrap the polygons at date iine
        wrapped_polygons=[]
        for polygon in reconstructed_polygons:
            if date_line_wrapper:
                wrapped_polygons.extend(date_line_wrapper.wrap(polygon.get_reconstructed_geometry(),2.0))
            else:
                wrapped_polygons.append(polygon.get_reconstructed_geometry())

        polygons=[]
        for p in wrapped_polygons: 
            if date_line_wrapper:
                points = [[point.to_lat_lon()[1],point.to_lat_lon()[0]] \
                    for point in p.get_exterior_points()]
            else:
                points = [[point.to_lat_lon()[1],point.to_lat_lon()[0]] \
                    for point in p.get_exterior_ring_points()]
            polygons.append(Polygon(points))

        ax.add_geometries(polygons, ccrs.PlateCarree(), 
                edgecolor=edgecolor, 
                facecolor=facecolor, alpha=float(alpha))
        fig.savefig(imgdata, format='png', bbox_inches='tight',dpi=96, transparent=True, pad_inches=0)
        imgdata.seek(0)  # rewind the data
        plt.clf()

        return HttpResponse(imgdata.getvalue(), content_type="image/png")
    except Exception as e:
        #raise e
        print(str(e))
        red = Image.new('RGBA', (512, 512), (255,100,100,100))
        response = HttpResponse(content_type="image/png")
        red.save(response, "PNG")
        return response