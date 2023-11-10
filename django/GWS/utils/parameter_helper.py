def get_pids(params, count):
    """
    return a list of plate IDs
    """
    pids_str = params.get("pids", None)
    pid_str = params.get("pid", None)
    pids = []
    try:
        if pids_str:
            pids = pids_str.split(",")
            pids = [int(i) for i in pids]
            if len(pids) != count:
                raise Exception(
                    "The number of plate ids must be the same with the number of points."
                )
        else:
            if pid_str:
                pids = count * [int(pid_str)]
            else:
                pids = count * [None]
    except ValueError as e:
        raise Exception(f"Invalid plate ID value ({e}).")
    return pids


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


def get_float(params, param_name: str, default=None):
    """get a float number from params for the given param_name, return None if invalid or non-exist"""
    number = params.get(param_name, default)
    if number is not None:
        try:
            number = float(number)
        except ValueError:
            print(f"Invalid floating point number: {param_name}({number})")
            number = default

    return number


def get_int(params, param_name: str, default=None):
    """get an integer number from params for the given param_name, return None if invalid or non-exist"""
    number = params.get(param_name, default)
    if number is not None:
        try:
            number = int(number)
        except ValueError:
            print(f"Invalid integer number: {param_name}({number})")
            number = default

    return number
