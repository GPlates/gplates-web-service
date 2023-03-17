import logging
import math
import json
import traceback

from django.db import connection
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseServerError)

logger = logging.getLogger("dev")


def query(request):
    '''
    Query a single value from raster by lon, lat
    http://localhost:18000/raster/query?lon=90&lat=-20&raster_name=age_grid

    Query some values from raster by lons, lats
    http://localhost:18000/raster/query?raster_name=crustal_thickness&lons=120,50,40&lats=45,67,-89

    query multiple points from raster
    the input points are like 
    lons: lon_0, lon_1,...,lon_n
    lats: lat_0, lat_1,...,lat_n
    '''

    raster_name = request.GET.get("raster_name", None)
    if not raster_name:
        return HttpResponseBadRequest("The 'raster_name' parameter must present in request!")

    try:
        lon = float(request.GET["lon"])
        lat = float(request.GET["lat"])
    except:
        lon = None
        lat = None

    try:
        lons_str = request.GET["lons"]
        lats_str = request.GET["lats"]
        lons = [float(i) for i in lons_str.split(',')]
        lats = [float(i) for i in lats_str.split(',')]
    except:
        lons = None
        lats = None

    format = request.GET.get("fmt", None)

    # lon = (lon + 360)%360

    # for a single location
    if lon is not None and lat is not None:
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
                # print(row)
                if format == 'json':
                    if row:
                        ret = {'lon': lon, 'lat': lat, 'value': row[1]}
                    else:
                        ret = {'lon': lon, 'lat': lat, 'value': math.nan}
                    response = HttpResponse(ret)
                    response = HttpResponse(json.dumps(ret),
                                            content_type='application/json')
                else:
                    if row:
                        ret = row[1]
                    else:
                        ret = "nan"
                    response = HttpResponse(ret)
        except:
            logger.error(traceback.format_exc())
            return HttpResponseServerError("Failed to query a single value from the raster.")
    # for multiple locations
    elif lons is not None and lats is not None:
        try:
            query_str = "   WITH pairs(x, y) AS (VALUES "
            for lon, lat in zip(lons, lats):
                query_str += f"({lon},{lat}),"
            query_str = query_str[:-1]
            query_str += f""")
            SELECT
                x,y,ST_Value(rast, ST_SetSRID(ST_MakePoint(x, y), 4326)) AS value
            FROM {raster_name} rs
                CROSS JOIN pairs
                WHERE ST_Intersects(rs.rast,  ST_SetSRID(ST_MakePoint(x, y), 4326));
            """
            # print(query_str)
            with connection.cursor() as cursor:
                cursor.execute(query_str)
                rows = cursor.fetchall()
                print(rows)
                ret = []
                for lon, lat in zip(lons, lats):
                    value = math.nan
                    for row in rows:
                        if math.isclose(lon, row[0]) and math.isclose(lat, row[1]):
                            value = row[2]
                            break
                    ret.append({'lon': lon, 'lat': lat, 'value': value})
                response = HttpResponse(ret)
                response = HttpResponse(json.dumps(ret),
                                        content_type='application/json')

        except:
            logger.error(traceback.format_exc())
            return HttpResponseServerError(f"Failed to query multiple locations from raster. {query_str}")
    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
