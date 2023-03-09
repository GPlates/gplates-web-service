import _rotation as rotation
import json
import math


from django.http import (HttpResponse, HttpResponseBadRequest)


def rotate(request):
    '''
    http://localhost:18000/rotation/rotate/?point=120,45&axis=20,-45&angle=20
    '''
    point_str = request.GET.get('point', None)
    axis_str = request.GET.get('axis', None)
    angle_str = request.GET.get('angle', None)
    if not point_str or not axis_str:
        return HttpResponseBadRequest("One point, one axis and angle are required in the request!")
    try:
        point = point_str.split(',')
        axis = axis_str.split(',')

        lon_point = float(point[0])
        lat_point = float(point[1])
        lon_axis = float(axis[0])
        lat_axis = float(axis[1])

        angle = float(angle_str)
    except:
        return HttpResponseBadRequest("Invalid points, axis or angle!")

    new_point = rotation.rotate((math.radians(lat_point), math.radians(
        lon_point)), (math.radians(lat_axis), math.radians(lon_axis)), angle)

    ret = {'point': (math.degrees(new_point[1]), math.degrees(
        new_point[0]))}

    response = HttpResponse(json.dumps(ret),
                            content_type='application/json')

    response['Access-Control-Allow-Origin'] = '*'
    return response
