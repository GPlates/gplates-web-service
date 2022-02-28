# -*- coding: utf-8 -*-


from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.db import connection

import logging, traceback, math
logger = logging.getLogger('dev')

def query(request):
    try:
        lon = float(request.GET['lon'])
        lat = float(request.GET['lat'])
        raster_name = request.GET['raster_name']
    except:
        logger.error(traceback.format_exc())
        return HttpResponseBadRequest('Bad raster query!')

    #lon = (lon + 360)%360   
 
    try:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT rid,ST_Value(rast, ST_SetSRID(ST_MakePoint({0},{1}),4326), false) AS val
                FROM public.{2}
                WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint({0},{1}),4326))'''.format(lon, lat, raster_name)
            )
            row = cursor.fetchone()
            
            ret='nan'
            if row:
                ret = row[1]
                if not math.isnan(ret) and ret >= 0:        
                    ret = '%.2f' % ret 
                
            response = HttpResponse(ret)
            #TODO: 
            #The "*" makes the service wide open to anyone. We should implement access control when time comes. 
            response['Access-Control-Allow-Origin'] = '*'
            return response
    except:
        logger.error(traceback.format_exc())    
        return HttpResponseServerError('Failed to query raster.')
    
