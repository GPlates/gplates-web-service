#
# return string for float numbers recursively
# round to "decimals" decimals
#
def round_floats(obj, decimals=4):
    if isinstance(obj, float):
        return round(obj, decimals)
    elif isinstance(obj, dict):
        return dict((k, round_floats(v)) for k, v in list(obj.items()))
    elif isinstance(obj, (list, tuple)):
        return list(map(round_floats, obj))
    return obj
