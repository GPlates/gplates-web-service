from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from StringIO import StringIO

# Create your views here.

import numpy as np
from utils.create_gpml import create_gpml_crustal_thickness
from utils.sphere_tools import random_points_on_sphere,sampleOnSphere,healpix_mesh


def litho1(request):

    mode = request.GET.get('mode', 'random_points')
    filename = request.GET.get('filename', 'litho1_scalar_coverage.gpmlz')
    if mode=='healpix':
        N = request.GET.get('N', 64)
    else:
        N = request.GET.get('N', 100000)

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
