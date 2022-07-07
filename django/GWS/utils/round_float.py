#
# return string for float number
# round to 4 decimals
#
def round_floats(obj):
    if isinstance(obj, float):
        return round(obj, 4)
    elif isinstance(obj, dict):
        return dict((k, round_floats(v)) for k, v in list(obj.items()))
    elif isinstance(obj, (list, tuple)):
        return list(map(round_floats, obj))             
    return obj