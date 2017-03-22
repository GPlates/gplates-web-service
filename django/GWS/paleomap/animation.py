import os, sys

path = '/var/www/gplates/gplates_web/gplates_web'
print 'Using DB settings in '+path
if path not in sys.path:
    sys.path.insert(0, path)
import settings

print settings.DATABASES
print settings.TMP_DIR

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed

import urllib, base64, StringIO

import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection
import matplotlib.animation as animation

from PIL import Image

import numpy as np

from views import reconstruct_coastlines

if not os.path.isdir(settings.TMP_DIR + '/animations'):
    os.mkdir(settings.TMP_DIR + '/animations')    


def update_frame(num,m):
    plt.cla()
    m = Basemap(projection='robin',lon_0=0.0,resolution='c')
    m.drawparallels(np.arange(-90.,91.,15.), labels=[True,True,False,False], color='black', fontsize=9, dashes=[1,0.1], linewidth=0.2)
    m.drawmeridians(np.arange(-180.,181.,60.), labels=[False,False,False,True], color='black', fontsize=9, dashes=[1,0.1], linewidth=0)
    m.drawmeridians(np.arange(-180.,181.,15.), labels=[False,False,False,0], color='black', fontsize=6, dashes=[1,0.1], linewidth=0.2)

    plt.title('{0} Ma'.format(num), fontsize=25)
    polygons = reconstruct_coastlines(num)
    for p in polygons:
        x,y = m([x[1] for x in p.get_reconstructed_geometry().to_lat_lon_list()],
                [x[0] for x in p.get_reconstructed_geometry().to_lat_lon_list()])
        plt.gca().add_patch(Polygon(list(zip(x,y)), edgecolor='black', facecolor='green', alpha=0.7))
    return plt.gcf(),


def init_frame():
    return plt.gcf(),


def generate(request):
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=2, metadata=dict(artist='Me'), bitrate=1800)
    
    try:
        m = Basemap(projection='robin',lon_0=0.0,resolution='c')
        m.drawparallels(np.arange(-90.,91.,15.), labels=[True,True,False,False], color='black', fontsize=9, dashes=[1,0.1], linewidth=0.2)
        m.drawmeridians(np.arange(-180.,181.,60.), labels=[False,False,False,True], color='black', fontsize=9, dashes=[1,0.1], linewidth=0)
        m.drawmeridians(np.arange(-180.,181.,15.), labels=[False,False,False,0], color='black', fontsize=6, dashes=[1,0.1], linewidth=0.2)

        fig = plt.gcf()
        ani = animation.FuncAnimation(fig, update_frame, 20, init_func=init_frame,fargs=(m,),
                                   interval=500, blit=True)
        #ani.save(settings.TMP_DIR + '/animations/test.mp4', writer=writer)
        response = HttpResponse(ani.to_html5_video())
        return response
    except Exception as e: 
        print str(e)
        red = Image.new('RGBA', (512, 512), (255,0,0,0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response

        #return HttpResponse('data:image/png;base64,' + urllib.quote(base64.b64encode(imgdata.buf)))

