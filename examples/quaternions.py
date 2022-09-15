from math import *


def normalize(v, tolerance=0.00001):
    mag2 = sum(n * n for n in v)
    if abs(mag2 - 1.0) > tolerance:
        mag = sqrt(mag2)
        v = tuple(n / mag for n in v)
    return v


def quat_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return w, x, y, z


def quat_conjugate(q):
    q = normalize(q)
    w, x, y, z = q
    return (w, -x, -y, -z)


def quat_vec_mult(q1, v1):
    v1 = normalize(v1)
    q2 = (0.0,) + v1
    return quat_mult(quat_mult(q1, q2), quat_conjugate(q1))[1:]


def axis_angle_to_quat(v, theta):
    v = normalize(v)
    x, y, z = v
    theta /= 2
    w = cos(theta)
    x = x * sin(theta)
    y = y * sin(theta)
    z = z * sin(theta)
    return w, x, y, z


def quat_to_axis_angle(q):
    w, v = q[0], q[1:]
    theta = acos(w) * 2.0
    return normalize(v), theta


def lat_lon_to_cart(lat, lon):
    x = cos(lat) * cos(lon)
    y = cos(lat) * sin(lon)
    z = sin(lat)
    return x, y, z


def cart_to_lat_lon(x, y, z):
    lat = asin(z)
    lon = atan2(y, x)
    return lat, lon


# point: lat lon coordinates
# axis:  lat lon coordinates
# angle: degree
# return: lat lon
def rotate(point, axis, angle):
    v = lat_lon_to_cart(radians(point[0]), radians(point[1]))
    axis = lat_lon_to_cart(radians(axis[0]), radians(axis[1]))
    quat = axis_angle_to_quat(axis, radians(angle))
    ret = quat_vec_mult(quat, v)
    ret_lat_lon = cart_to_lat_lon(ret[0], ret[1], ret[2])
    return degrees(ret_lat_lon[0]), degrees(ret_lat_lon[1])


def main():
    print(rotate([12, 34], [90, 0], 34))


if __name__ == "__main__":
    main()
