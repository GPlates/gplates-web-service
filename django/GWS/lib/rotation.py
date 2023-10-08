#
# a collection of rotation related functions
#


import math
import quaternions


def cross(a, b):
    '''
    cross product of two vectors defined only in three-dimensional space
    https://www.mathsisfun.com/algebra/vectors-cross-product.html
    https://en.wikipedia.org/wiki/Cross_product#Computing
    '''

    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]
    return c


def dot(a, b):
    '''
    dot product of two vectors
    https://www.mathsisfun.com/algebra/vectors-dot-product.html
    '''
    return sum(i*j for i, j in zip(a, b))


def find_axis_and_angle(point_a, point_b):
    '''
    given two points point_a and point_b in (lat, lon) format in radians
    return axis and angle in radians
    '''
    # get 3D vectors
    a_v = quaternions.lat_lon_to_cart(point_a[0], point_a[1])
    b_v = quaternions.lat_lon_to_cart(point_b[0], point_b[1])

    ab_cross = quaternions.normalize(cross(a_v, b_v))
    ab_dot = dot(a_v, b_v)

    axis = quaternions.cart_to_lat_lon(*ab_cross)  # in radians
    angle = math.acos(ab_dot)  # in radians

    return axis, angle


def rotate(point, axis, angle):
    '''
    rotate a point by axis and angle
    point: (lat, lon) in radians
    axis: (radian, radian)
    angle: radian
    return new point(lat, lon) in radians
    '''
    v = quaternions.lat_lon_to_cart(point[0], point[1])
    axis = quaternions.lat_lon_to_cart(axis[0], axis[1])
    quat = quaternions.axis_angle_to_quat(axis, angle)
    ret = quaternions.quat_vec_mult(quat, v)
    ret_lat_lon = quaternions.cart_to_lat_lon(ret[0], ret[1], ret[2])
    return (ret_lat_lon[0], ret_lat_lon[1])


def interp_two_points(point_a, point_b, num=10):
    '''
    interpolate between two points(in radians) along the great circle
    return a list of points in between(in radians)
    '''
    ret = [point_a]
    axis, angle = find_axis_and_angle(point_a, point_b)
    for angle_ in [(angle/num)*i for i in range(1, num+1)]:
        lat, lon = rotate(point_a,
                          axis,
                          angle_)
        ret.append((lat, lon))

    return ret


def distance(point_a, point_b, earth_radius=6378.14):
    '''
    calculate the distance between to points (lat, lon) in radians
    '''
    _, angle = find_axis_and_angle(point_a, point_b)
    return angle*earth_radius


if __name__ == "__main__":
    # test
    # 1. find axis and angle between two points a and b
    # 2. use the axis and angle to rotate point a
    # 3. check if the rotation ends up at point b
    point_a = tuple((math.radians(i) for i in (45, 20)))  # lat, lon
    point_b = tuple((math.radians(i) for i in (-45, 120)))

    axis, angle = find_axis_and_angle(point_a, point_b)

    print(axis, angle)

    point_b_new = rotate(point_a, axis, angle)

    # check if the two points are the same
    print(tuple(round(math.degrees(i), 2) for i in point_b_new))
    print(tuple(round(math.degrees(i), 2) for i in point_b))

    # intepolate between point a and b
    points_in_between = interp_two_points(point_a, point_b)
    with open('interpolation.gmt', 'w+') as f:
        for p in points_in_between:
            f.write(f"{math.degrees(p[1]):.2f} {math.degrees(p[0]):.2f}\n")

    print(distance(point_a, point_b))
    print('test finished!')
