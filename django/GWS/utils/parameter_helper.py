#
# a bunch of helper function to deal with parameters in http request
#
import json
import logging

logger = logging.getLogger("default")


def get_time(params, name="time"):
    """
    get reconstruction time from http request
    """
    time = params.get(name, None)
    timef = 0.0
    if not time:
        raise Exception('The "time" parameter cannot be empty.')

    try:
        timef = float(time)
    except:
        raise Exception(f'The "time" parameter is invalid ({time}).')
    return timef


def get_anchor_plate_id(params):
    """
    get anchor plate id from http request
    """
    anchor_plate_id = params.get("anchor_plate_id", 0)

    try:
        return int(anchor_plate_id)
    except:
        raise Exception(
            f'The "anchor_plate_id" parameter is invalid ({anchor_plate_id}).'
        )


def get_float(params, param_name: str, default):
    """get a float number from params for the given param_name, return default if invalid or non-exist"""
    number = params.get(param_name, default)
    try:
        number = float(number)
    except (ValueError, TypeError):
        print(
            f"Invalid floating point number: {param_name}({number}), using default value {default}"
        )
        number = default
    if not isinstance(number, float) and number is not None:
        raise Exception(
            f"Invalid floating point number parameter: {param_name}({number}) and invalid default value {default}"
        )
    return number


def get_int(params, param_name: str, default):
    """get an integer number from params for the given param_name, return default if invalid or non-exist"""
    number = params.get(param_name, default)
    try:
        number = int(number)
    except (ValueError, TypeError):
        logger.debug(
            f"Invalid integer number: {param_name}({number}), using default value {default}"
        )
        number = default
    if not isinstance(number, int) and number is not None:
        raise Exception(
            f"Invalid integer number parameter: {param_name}({number}) and the default value {default} is also invalid."
        )
    return number


def get_bool(params, param_name: str, default: bool):
    """get boolean value from params for the given param_name, return default if invalid or non-exist.
    return true if the param_name exists but empty, such as "&return_null_points"
    """
    flag = params.get(param_name, default)
    if isinstance(flag, str):
        if flag == "":
            return True
        if flag.lower() == "true":
            flag = True
        elif flag.lower() == "false":
            flag = False
        elif flag.lower() == "0":
            flag = False
        elif flag.lower() == "1":
            flag = True
        else:
            print(
                f"Invalid boolean value: {param_name}({flag}). Use the default value {default}"
            )
            flag = default
    if not isinstance(flag, bool):
        raise Exception(
            f"Invalid boolean parameter: {param_name}({flag}) and invalid default value {default}"
        )
    return flag


def get_int_list(params, param_name: str):
    """get an integer list from params for the given param_name, return [] if invalid or non-exist"""
    return get_value_list(params, param_name, int)


def get_value_list(params, param_name: str, value_type: type):
    """get a list of values from params for the given param_name, return [] if invalid or non-exist"""
    param_str = params.get(param_name, "")
    try:
        items = param_str.split(",")
        return [value_type(i) for i in items if len(i.strip()) > 0]
    except (ValueError, TypeError):
        print(f"Invalid parameter {param_name}:{param_str}.")
        return []


def get_lats_lons(params):
    """return two lists, one is the lats and the other is lons

    supported parameter format:

    lats=33,44,55
    lons=100,50,0

    lats=[33,44,55]
    lons=[100,50,0]

    lat=33
    lon=100

    points=100,33,50,44,0,55
    points=[100,33,50,44,0,55]
    points=[[100,33],[50,44],[0,55]]

    point=100,33
    point=[100,33]

    preference: lats&lons > lat&lon > points > point
    """
    points_str = params.get("points", None)
    lats_str = params.get("lats", None)
    lons_str = params.get("lons", None)
    point_str = params.get("point", None)
    lat_str = params.get("lat", None)
    lon_str = params.get("lon", None)
    lats = []
    lons = []

    if lats_str and lons_str:
        if not lats_str.startswith("["):
            lats_str = "[" + lats_str
        if not lats_str.endswith("]"):
            lats_str = lats_str + "]"

        if not lons_str.startswith("["):
            lons_str = "[" + lons_str
        if not lons_str.endswith("]"):
            lons_str = lons_str + "]"
        try:
            lats = json.loads(lats_str)
            lons = json.loads(lons_str)
        except Exception as e:
            logger.warning(str(e))
            raise Exception(
                f"Invalid 'lats' and/or 'lons' parameters. lats:({lats_str}), lons:({lons_str})."
            )
        if len(lats) != len(lons):
            raise Exception(
                f"The 'lats' and 'lons' must have the same length lats:{lats_str}({len(lats)})), lons:{lons_str}({len(lons)}))."
            )
    elif lat_str and lon_str:
        try:
            lats.append(float(lat_str))
            lons.append(float(lon_str))
        except Exception as e:
            logger.warning(str(e))
            raise Exception(
                f"Invalid 'lat' and/or 'lon' parameters. lat:({lat_str}), lon:({lon_str})."
            )
    elif points_str:
        if not points_str.startswith("["):
            points_str = "[" + points_str
        if not points_str.endswith("]"):
            points_str = points_str + "]"
        try:
            ps = json.loads(points_str)
        except Exception as e:
            logger.warning(str(e))
            raise Exception(f"Invalid 'points' parameter. points:({points_str})")
        ps_len = len(ps)
        if ps_len == 0:
            raise Exception(f"The 'points' parameter is empty. points:({points_str})")

        if isinstance(ps[0], list):
            for p in ps:
                try:
                    lats.append(float(p[1]))
                    lons.append(float(p[0]))
                except Exception as e:
                    logger.warning(str(e))
                    raise Exception(f"Invalid coordinates are found. ({p})")
        else:
            if ps_len % 2 == 0:
                try:
                    lats = [float(p) for p in ps[1::2]]
                    lons = [float(p) for p in ps[0::2]]
                except Exception as e:
                    logger.warning(str(e))
                    raise Exception(f"Invalid coordinates are found. points:({ps})")
            else:
                raise Exception(
                    f"Invalid 'points' parameter. The longitude and latitude should come in pairs ({points_str})."
                )
    elif point_str:
        if not point_str.startswith("["):
            point_str = "[" + point_str
        if not point_str.endswith("]"):
            point_str = point_str + "]"
        try:
            p = json.loads(point_str)
            lats.append(float(p[1]))
            lons.append(float(p[0]))
        except Exception as e:
            logger.warning(str(e))
            raise Exception(f"Invalid 'point' parameter. point:({point_str})")
    else:
        raise Exception(
            f"Unable to get lats and lons from the request's parameter. points:{points_str} lats:{lats_str} lons:{lons_str} lon:{lon_str} lat:{lat_str} point:{point_str}"
        )

    for lon in lons:
        if lon > 180 or lon < -180:
            raise Exception(f"Invalid longitude is found {lon}.")
    for lat in lats:
        if lat > 90 or lat < -90:
            raise Exception(f"Invalid latitude is found {lat}.")

    return lats, lons
