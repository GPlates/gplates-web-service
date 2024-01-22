#
# a bunch of helper function to deal with parameters in http request
#


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
        print(
            f"Invalid integer number: {param_name}({number}), using default value {default}"
        )
        number = default
    if not isinstance(number, int) and number is not None:
        raise Exception(
            f"Invalid integer number parameter: {param_name}({number}) and invalid default value {default}"
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
    """return two lists, one is the lats and the other is lons"""
    points_str = params.get("points", None)
    lats_str = params.get("lats", None)
    lons_str = params.get("lons", None)
    lats = []
    lons = []
    if points_str:
        # filter out invalid characters
        # points_str = "".join(c for c in points_str if c.isdecimal()
        #                     or (c in [".", ",", "-"]))
        ps = points_str.split(",")
        ps_len = len(ps)
        if ps_len > 0 and ps_len % 2 == 0:
            lats = ps[1::2]
            lons = ps[0::2]
        else:
            raise Exception(
                f"Invalid 'points' parameter. The longitude and latitude should come in pairs ({points_str})."
            )
    else:
        if lats_str and lons_str:
            lats = lats_str.split(",")
            lons = lons_str.split(",")
            if len(lats) != len(lons):
                raise Exception(
                    f"Invalid 'lats' and 'lons' parameter. ({lats_str}), ({lons_str})."
                )
    if lats and lons:
        try:
            lats = [float(i) for i in lats]
            lons = [float(i) for i in lons]
        except:
            raise Exception(f"Invalid coordinates. ({lats_str}), ({lons_str}).")
    return lats, lons
