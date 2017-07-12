
from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, 
    HttpResponseBadRequest, HttpResponseServerError, 
    HttpResponseNotAllowed)

from django.conf import settings

import urllib, base64, StringIO, os, string, random
from datetime import datetime
import subprocess

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

TMP_DIR='/tmp/gws'

def create(request):
    time = request.GET.get('time', 140) 
    model = request.GET.get('model',settings.MODEL_DEFAULT)
    anchor_plate_id = request.GET.get('pid', 0)
    proj = request.GET.get('proj', 'Equirectangular')    
    engine = request.GET.get('engine', 'GMT')
    animation = request.GET.get('animation', False)
    fmt = request.GET.get('fmt', 'png')    

    tmp_dir=(TMP_DIR+'/'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f_')+
        ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7)))
    os.mkdir(tmp_dir)

    try:
        if animation.lower()=='true' or animation.lower() == '1':
            animation = True
        else:
            animation = False
    except:
        pass

    if engine.lower() == 'matplotlib':
        return create_matplotlib(model, time, proj, anchor_plate_id)
    else:
        if animation:
            cnt = 0
            for t in xrange(20,-1,-2):
                create_gmt(model, t, proj, anchor_plate_id, tmp_dir, cnt)
                cnt+=1
            subprocess.call('/usr/bin/ffmpeg -r 3 -i {0}/img-%4d.png {0}/movie.mp4'.format(tmp_dir),shell=True)
            with open(tmp_dir+'/movie.mp4', "rb") as image_file:
                return  HttpResponse(image_file.read(),content_type='video/mp4')
        else:
            return create_gmt(model, time, proj, anchor_plate_id, tmp_dir, fmt=fmt)


def create_gmt(model, time, proj, anchor_plate_id, tmp_dir,cnt=0,fmt='png'):
    data = get_reconstruction_model_dict(model)
    shp_path = settings.MODEL_STORE_DIR+model+'/'+data['Coastlines']
    input_rotation_filename = []
    for f in data['RotationFile']:
        input_rotation_filename.append((settings.MODEL_STORE_DIR+model+ '/'+f).encode('utf-8','ignore'))
    output_coastlines_filename = tmp_dir+'/coastlines.gmt'
    pygplates.reconstruct(
        shp_path.encode('utf-8','ignore'),
        input_rotation_filename,
        output_coastlines_filename,
        int(time),
        int(anchor_plate_id))
    #proj = '-JX20c/10c'
    if proj.lower() == 'robinson':
        projc = '-JN20c'
    elif proj.lower() == 'mollweide':
        projc = '-JW20c'
    else:
        projc = '-JQ20c'

    file_base_name = 'img-{:04d}'.format(cnt)
    os.system('gmt psbasemap -R-180/180/-90/90 {0} -K -Bafg -B+t\"{2}Ma\" > {1}/{3}.ps'.format(projc, tmp_dir, time, file_base_name))
    os.system('gmt psxy -Rd {0} -W0.25p,grey10 -K -O -m {1}/coastlines.gmt -V >> {1}/{2}.ps'.format(projc, tmp_dir, file_base_name))
    os.system('gmt psclip /usr/src/clip.txt -Rd {0} -O -V  >> {1}/{2}.ps'.format(projc,tmp_dir, file_base_name))
    os.system('cd {0} && gmt psconvert {0}/{1}.ps -A -E240 -Tg -P'.format(tmp_dir,file_base_name))
       
    try:
        with open(tmp_dir+'/{0}.png'.format(file_base_name), "rb") as image_file:
            if fmt == 'base64':
                response = HttpResponse('data:image/png;base64,' + urllib.quote(base64.b64encode(image_file.read())))
            else:
                response = HttpResponse(image_file.read(),content_type='image/png')
            response['Access-Control-Allow-Origin'] = '*'
            return response 
    except Exception as e:
        return HttpResponseServerError(str(e))



def create_matplotlib(model, time, proj, anchor_plate_id):
    try:
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

