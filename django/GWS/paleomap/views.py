from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings

import urllib, base64, StringIO, os 

import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection

from PIL import Image

import numpy as np

import pygplates

from utils.get_model import get_reconstruction_model_dict

def create(request):
	shp_path = settings.MODEL_STORE_DIR+'/'+settings.MODEL_DEFAULT+'/coastlines_low_res/Seton_etal_ESR2012_Coastlines_2012.shp'
	input_rotation_filename = settings.MODEL_STORE_DIR+'/'+settings.MODEL_DEFAULT+ '/Seton_etal_ESR2012_2012.1.rot'
	output_coastlines_filename = '/tmp/coastlines.gmt'
	pygplates.reconstruct(shp_path,input_rotation_filename,output_coastlines_filename,100)
	proj = '-JX20c/10c'
	print os.getcwd()
	os.system('gmt psxy -Rd %s -W0.25p,grey10 -K -m /tmp/coastlines.gmt -V > /tmp/test.ps' % (proj))
	os.system('gmt psclip /usr/src/clip.txt -Rd %s -O -V  >> /tmp/test.ps' % (proj))
	os.system('cd /tmp && gmt psconvert /tmp/test.ps -A -E240 -Tj -P')
	
	return HttpResponse('OK')

def create_1(request):
    try:
        time = request.GET.get('time', 140)
        m = Basemap(projection='robin',lon_0=0.0,resolution='c')
        m.drawparallels(np.arange(-90.,91.,15.), labels=[True,True,False,False], color='black', fontsize=9, dashes=[1,0.1], linewidth=0.2)
        m.drawmeridians(np.arange(-180.,181.,30.), labels=[False,False,False,True], color='black', fontsize=9, dashes=[1,0.1], linewidth=0.1)
        m.drawmeridians(np.arange(-180.,181.,15.), labels=[False,False,False,0], color='black', fontsize=6, dashes=[1,0.1], linewidth=0.2)
        
        fig = plt.gcf()
        fig.set_size_inches(16,8)
        imgdata = StringIO.StringIO()

        plt.title('{0} Ma'.format(time), fontsize=25)
        polygons = reconstruct_coastlines(time)    
        for p in polygons:   
            x,y = m([x[1] for x in p.get_reconstructed_geometry().to_lat_lon_list()],
                    [x[0] for x in p.get_reconstructed_geometry().to_lat_lon_list()]) 
            plt.gca().add_patch(Polygon(list(zip(x,y)), edgecolor='black', facecolor='green', alpha=0.7))

        fig.savefig(imgdata, format='png', bbox_inches='tight',dpi=96)
        imgdata.seek(0)  # rewind the data
        plt.clf()
 
        return HttpResponse(imgdata.buf, content_type="image/jpeg")
    except Exception as e:
        print str(e)
        red = Image.new('RGBA', (512, 512), (255,0,0,0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response

        #return HttpResponse('data:image/png;base64,' + urllib.quote(base64.b64encode(imgdata.buf)))


def reconstruct_coastlines(time):
    shp_path = settings.MODEL_STORE_DIR+'/'+settings.MODEL_DEFAULT+'/coastlines_low_res/Seton_etal_ESR2012_Coastlines_2012.shp'

    import shapefile
    sf = shapefile.Reader(shp_path)
    features = []
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


    pygplates.reconstruct(
        feature_collection,
        rotation_model,
        reconstructed_polygons,
        float(time))

    return reconstructed_polygons

