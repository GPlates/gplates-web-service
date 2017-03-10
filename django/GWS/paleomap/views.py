from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed

import urllib, base64, StringIO 

import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection

from PIL import Image

import numpy as np

def create(request):
    try:
        m = Basemap(projection='robin',lon_0=0.0,resolution='c')
        m.drawparallels(np.arange(-90.,91.,15.), labels=[True,True,False,False], color='black', fontsize=9, dashes=[1,0.1], linewidth=0.2)
        m.drawmeridians(np.arange(-180.,181.,30.), labels=[False,False,False,True], color='black', fontsize=9, dashes=[1,0.1], linewidth=0)
        m.drawmeridians(np.arange(-180.,181.,15.), labels=[False,False,False,0], color='black', fontsize=6, dashes=[1,0.1], linewidth=0.2)
        
        fig = plt.gcf()
        fig.set_size_inches(16,8)
        imgdata = StringIO.StringIO()
        plt.title('{0} Ma'.format(0), fontsize=25, fontname="Open Sans")
        fig.savefig(imgdata, format='png', bbox_inches='tight',dpi=96)
        imgdata.seek(0)  # rewind the data
        plt.clf()
 
        return HttpResponse(imgdata.buf, content_type="image/jpeg")
    except:
        red = Image.new('RGBA', (512, 512), (255,0,0,0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response

        #return HttpResponse('data:image/png;base64,' + urllib.quote(base64.b64encode(imgdata.buf)))
