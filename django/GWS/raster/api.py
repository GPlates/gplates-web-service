import json
import logging
import math
import traceback

from django.db import connection
from django.db.utils import ProgrammingError
from django.http import HttpResponseBadRequest, HttpResponseServerError
from utils.access_control import get_client_ip
from utils.decorators import check_get_post_request_and_get_params, return_HttpResponse
from utils.parameter_helper import get_float, get_lats_lons

logger = logging.getLogger("default")
access_logger = logging.getLogger("queue")


@check_get_post_request_and_get_params
@return_HttpResponse()
def query(request, params={}):
    """Query a single value from raster by lon, lat
    http://localhost:18000/raster/query?lon=90&lat=-20&raster_name=crustal_thickness

    Query some values from raster by lons, lats
    http://localhost:18000/raster/query?raster_name=crustal_thickness&lons=120,50,40&lats=45,67,-89

    query multiple points from raster
    the input points are like
    lons: lon_0, lon_1,...,lon_n
    lats: lat_0, lat_1,...,lat_n

    :param fmt: return data format
        1. simple
        2. json
    """

    raster_name = params.get("raster_name", None)
    if not raster_name:
        return HttpResponseBadRequest(
            "The 'raster_name' parameter must present in the request!"
        )

    try:
        lats, lons = get_lats_lons(params)
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(str(e))

    format = request.GET.get("fmt", "simple").strip().lower()

    # lon = (lon + 360)%360

    try:
        query_str = None
        # for a single location
        if len(lats) == 1 and len(lons) == 1:
            lat = lats[0]
            lon = lons[0]
            with connection.cursor() as cursor:
                query_str = f"""SELECT rid,ST_Value(rast, ST_SetSRID(ST_MakePoint({lon},{lat}),4326), false) AS val
                    FROM raster.{raster_name}
                    WHERE ST_Intersects(rast, ST_SetSRID(ST_MakePoint({lon},{lat}),4326))"""
                cursor.execute(query_str)
                row = cursor.fetchone()
                ret_value = None
                if row is None or not isinstance(row[1], (int, float)):
                    ret_value = None
                else:
                    ret_value = round(row[1], 4)

                # print(row)
                if format == "json":
                    ret = {"lon": lon, "lat": lat, "value": ret_value}
                else:
                    ret = ret_value

                return json.dumps(ret)
        # for multiple locations
        elif lons and lats:
            query_str = "   WITH pairs(x, y) AS (VALUES "
            for lon, lat in zip(lons, lats):
                query_str += f"({lon},{lat}),"
            query_str = query_str[:-1]
            query_str += f""")
            SELECT
                x,y,ST_Value(rast, ST_SetSRID(ST_MakePoint(x, y), 4326)) AS value
            FROM raster.{raster_name} rs
                CROSS JOIN pairs
                WHERE ST_Intersects(rs.rast,  ST_SetSRID(ST_MakePoint(x, y), 4326));
            """
            # logger.debug(query_str)
            with connection.cursor() as cursor:
                cursor.execute(query_str)
                rows = cursor.fetchall()
                logger.debug(rows)
                ret = []
                for lon, lat in zip(lons, lats):
                    value = None
                    for row in rows:
                        if (
                            math.isclose(lon, row[0])
                            and math.isclose(lat, row[1])
                            and isinstance(row[2], (int, float))
                        ):
                            value = round(row[2], 4)
                            break
                    ret.append({"lon": lon, "lat": lat, "value": value})
                if format == "json":
                    return json.dumps(ret)
                else:
                    return json.dumps([x["value"] for x in ret])
    except ProgrammingError as e:
        logger.error(e)
        return HttpResponseServerError(
            f'The tabel "raster.{raster_name}" does not exist. Check if the raster name is correct. Use https://gws.gplates.org/raster/list to list all available rasters.'
        )
    except:
        logger.error(traceback.format_exc())
        logger.error(f"The query string is {query_str}.")
        return HttpResponseServerError(f"Failed to query raster: {raster_name}.")


@return_HttpResponse()
def list_all_rasters(request):
    """return all the raster names in DB
    select table_name from information_schema.tables where table_schema='raster';

    http://localhost:18000/raster/list
    """
    access_logger.info(get_client_ip(request) + f" {request.get_full_path()}")

    try:
        query_str = "  select table_name from information_schema.tables where table_schema='raster'; "

        with connection.cursor() as cursor:
            cursor.execute(query_str)
            rows = cursor.fetchall()
            logger.debug(rows)
            ret = [i[0] for i in rows]
            return json.dumps(ret)

    except:
        logger.error(traceback.format_exc())
        return HttpResponseServerError(f"Failed to list raster names.")
