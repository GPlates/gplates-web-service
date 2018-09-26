# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.db import connection

import logging, traceback
logger = logging.getLogger('dev')

def query(request):
    try:
        lon = float(request.GET['lon'])
        lat = float(request.GET['lat'])
        raster_name = request.GET['raster_name']
    except:
        logger.error(traceback.format_exc())
        return HttpResponseBadRequest('Bad raster query!')

    lon = (lon + 360)%360   
 
    with connection.cursor() as cursor:
        cursor.execute('''SELECT rid,ST_Value(rast, ST_SetSRID(ST_MakePoint({0},{1}),4326), false) AS val
            FROM public.{2}
            WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint({0},{1}),4326))'''.format(lon, lat, raster_name)
        )
        row = cursor.fetchone()
        if row:
            return HttpResponse(row[1])
        else:
            return HttpResponseServerError('Failed to query raster.')
    return HttpResponse("some incredible thing just happened!!!") 
