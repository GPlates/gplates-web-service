def get_pids(params, count):
    '''
    return a list of plate IDs
    '''
    pids_str = params.get("pids", None)
    pid_str = params.get("pid", None)
    pids = []
    try:
        if pids_str:
            pids = pids_str.split(",")
            pids = [int(i) for i in pids]
            if len(pids) != count:
                raise Exception(
                    "The number of plate ids must be the same with the number of points.")
        else:
            if pid_str:
                pids = count * [int(pid_str)]
            else:
                pids = count * [None]
    except ValueError as e:
        raise Exception(f"Invalid plate ID value ({e}).")
    return pids


def get_time(params):
    '''
    get reconstruction time from http request
    '''
    time = params.get("time", None)
    timef = 0.0
    if not time:
        raise Exception('The "time" parameter cannot be empty.')

    try:
        timef = float(time)
    except:
        raise Exception(
            f'The "time" parameter is invalid ({time}).'
        )
    return timef


def get_anchor_plate_id(params):
    '''
    get anchor plate id from http request
    '''
    anchor_plate_id = params.get("anchor_plate_id", 0)

    try:
        return int(anchor_plate_id)
    except:
        raise Exception(
            f'The "anchor_plate_id" parameter is invalid ({anchor_plate_id}).'
        )
