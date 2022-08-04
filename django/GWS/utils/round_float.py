#
# return string for float numbers recursively
# round to "decimals" decimals
#
def round_floats(obj, decimals=4):
    if isinstance(obj, float):
        return round(obj, decimals)
    elif isinstance(obj, dict):
        return dict((k, round_floats(v, decimals)) for k, v in list(obj.items()))
    elif isinstance(obj, (list, tuple)):
        return [round_floats(x, decimals) for x in obj]
    return obj
