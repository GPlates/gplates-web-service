import logging
import math
import traceback

from django.db import connection
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseServerError)

logger = logging.getLogger("dev")


def query(request):
    '''
    Query a single value from raster by lon, lat
    '''
    try:
        lon = float(request.GET["lon"])
        lat = float(request.GET["lat"])
        raster_name = request.GET["raster_name"]
    except:
        logger.error(traceback.format_exc())
        return HttpResponseBadRequest("Bad raster query!")

    # lon = (lon + 360)%360

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT rid,ST_Value(rast, ST_SetSRID(ST_MakePoint({0},{1}),4326), false) AS val
                FROM public.{2}
                WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint({0},{1}),4326))""".format(
                    lon, lat, raster_name
                )
            )
            row = cursor.fetchone()
            print(row)

            ret = "nan"
            if row:
                ret = row[1]
                if not math.isnan(ret) and ret >= 0:
                    ret = "%.2f" % ret

            response = HttpResponse(ret)
            # TODO:
            # The "*" makes the service wide open to anyone. We should implement access control when time comes.
            response["Access-Control-Allow-Origin"] = "*"
            return response
    except:
        logger.error(traceback.format_exc())
        return HttpResponseServerError("Failed to query raster.")


def query_multiple_points(request):
    '''
    http://localhost:18000/raster/query_m?raster=crustal_thickness&lons=120,50,40&lats=45,67,-89

    query multiple points from raster
    the input points are like 
    lons: lon_0, lon_1,...,lon_n
    lats: lat_0, lat_1,...,lat_n
    '''
    try:
        lons_str = request.GET["lons"]
        lats_str = request.GET["lats"]
        raster_name = request.GET["raster"]
        lons = [float(i) for i in lons_str.split(',')]
        lats = [float(i) for i in lats_str.split(',')]
    except:
        logger.error(traceback.format_exc())
        return HttpResponseServerError("Invalid request parameters.")

    
    query_str = "   WITH pairs(x, y) AS (VALUES "
    for lon, lat in zip(lons,lats):
        query_str += f"({lon},{lat}),"
    query_str = query_str[:-1]
    query_str += f""")
    SELECT
        ST_Value(rast, ST_SetSRID(ST_MakePoint(x, y), 4326)) AS value
    FROM {raster_name} rs
        CROSS JOIN pairs
        WHERE ST_Intersects(rs.rast,  ST_SetSRID(ST_MakePoint(x, y), 4326));
    """
    print(query_str)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query_str)
            rows = cursor.fetchall()
            print(rows)
    except:
        logger.error(traceback.format_exc())
        return HttpResponseServerError(f"Failed to query multiple locations from raster. {query_str}")

    ret=rows
    response = HttpResponse(ret)
    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
    