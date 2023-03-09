
import _rotation as rotation
import json
import math


from django.http import (HttpResponse, HttpResponseBadRequest)


def find_axis_and_angle(request):
    '''
    http://localhost:18000/earth/find_axis_and_angle/?point_a=120,45&point_b=20,-45
    '''
    point_a_str = request.GET.get('point_a', None)
    point_b_str = request.GET.get('point_b', None)
    if not point_a_str or not point_b_str:
        return HttpResponseBadRequest("Two points are required in the request!")
    try:
        point_a = point_a_str.split(',')
        point_b = point_b_str.split(',')

        lon_a = float(point_a[0])
        lat_a = float(point_a[1])
        lon_b = float(point_b[0])
        lat_b = float(point_b[1])
    except:
        return HttpResponseBadRequest("Invalid points!")

    axis, angle = rotation.find_axis_and_angle((math.radians(lat_a), math.radians(
        lon_a)), (math.radians(lat_b), math.radians(lon_b)))

    ret = {'axis': (math.degrees(axis[1]), math.degrees(
        axis[0])), "angle": math.degrees(angle)}

    response = HttpResponse(json.dumps(ret),
                            content_type='application/json')

    response['Access-Control-Allow-Origin'] = '*'
    return response


def interp_two_locations(request):
    '''
    http://localhost:18000/earth/interp_two_locations/?point_a=120,45&point_b=20,-45&num=10
    '''
    point_a_str = request.GET.get('point_a', None)
    point_b_str = request.GET.get('point_b', None)
    num_str = request.GET.get('num', 10)
    if not point_a_str or not point_b_str:
        return HttpResponseBadRequest("Two points are required in the request!")
    try:
        point_a = point_a_str.split(',')
        point_b = point_b_str.split(',')

        lon_a = float(point_a[0])
        lat_a = float(point_a[1])
        lon_b = float(point_b[0])
        lat_b = float(point_b[1])

        num = int(num_str)
    except:
        return HttpResponseBadRequest("Invalid points!")

    points_r = rotation.interp_two_points((math.radians(lat_a), math.radians(
        lon_a)), (math.radians(lat_b), math.radians(lon_b)), num)

    points_d = [[round(math.degrees(p[1]), 4), round(
        math.degrees(p[0]), 4)]for p in points_r]

    ret = {'locations': points_d}

    response = HttpResponse(json.dumps(ret),
                            content_type='application/json')

    response['Access-Control-Allow-Origin'] = '*'
    return response


def distance(request):
    '''
    http://localhost:18000/earth/distance/?point_a=120,45&point_b=20,-45
    '''
    point_a_str = request.GET.get('point_a', None)
    point_b_str = request.GET.get('point_b', None)

    if not point_a_str or not point_b_str:
        return HttpResponseBadRequest("Two points are required in the request!")
    try:
        point_a = point_a_str.split(',')
        point_b = point_b_str.split(',')

        lon_a = float(point_a[0])
        lat_a = float(point_a[1])
        lon_b = float(point_b[0])
        lat_b = float(point_b[1])

    except:
        return HttpResponseBadRequest("Invalid points!")

    distance = rotation.distance((math.radians(lat_a), math.radians(
        lon_a)), (math.radians(lat_b), math.radians(lon_b)))

    ret = {'distance': distance}

    response = HttpResponse(json.dumps(ret),
                            content_type='application/json')

    response['Access-Control-Allow-Origin'] = '*'
    return response
