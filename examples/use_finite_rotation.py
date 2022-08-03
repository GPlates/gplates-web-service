# in the root folder, run
# ``docker run -it --rm -v `pwd`:/gws gplates/gws /bin/bash -c "/usr/bin/python3 /gws/examples/use_finite_rotation.py"``
# alternatively
# open this script in vs code
# connect to gplates web service docker container
# run it inside vs code
import json
import os
import random
import math

import pygplates
import requests

import quaternions

SERVER_URL = "http://localhost:80"
# SERVER_URL = "https://gws.gplates.org"
time = 100.0

# get all the plate IDs in the reconstruction tree at 100Ma
url = f"{SERVER_URL}/rotation/get_plate_ids?time=100"
r = requests.get(url)
pids = json.loads(r.text)
# print(pids)

# pick up a random plate ID from above plate IDs
random_pid = pids[random.randint(0, len(pids) - 1)]
# print(random_pid)

# define a random test point
test_point = [random.randint(-90, 90), random.randint(-180, 180)]  # lat, lon

script_path = os.path.dirname(os.path.realpath(__file__))
rotation_model = pygplates.RotationModel(
    f"{script_path}/../django/GWS/DATA/MODELS/SETON2012/Seton_etal_ESR2012_2012.1.rot"
)  # use the default rotation model

# rotate the test point with pygplates
rotated_points = rotation_model.get_rotation(
    float(time), random_pid
) * pygplates.PointOnSphere(test_point)
print("pygplates:")
print(rotated_points.to_lat_lon())

# rotate with euler pole and angle
url = f"{SERVER_URL}/rotation/get_euler_pole_and_angle?times={time}&pids={random_pid}"
# print(url)
r = requests.get(url)
pole_and_angle = json.loads(r.text)
pole_and_angle = pole_and_angle[str(float(time))][str(random_pid)]
print("euler pole and angle:")
print(
    quaternions.rotate(
        test_point, [pole_and_angle[1], pole_and_angle[0]], pole_and_angle[2]
    )  # test point[lat,lon], pole[lat, lon], angle(degree)
)

# rotate with quaternions
url = f"{SERVER_URL}/rotation/get_quaternions?times={time}&pids={random_pid}"
# print(url)
r = requests.get(url)
quat = json.loads(r.text)
quat = quat[str(float(time))][str(random_pid)]
v = quaternions.lat_lon_to_cart(
    math.radians(test_point[0]), math.radians(test_point[1])
)
ret = quaternions.quat_vec_mult(quat, v)
ret_lat_lon = quaternions.cart_to_lat_lon(ret[0], ret[1], ret[2])
print("quaternions:")
print(math.degrees(ret_lat_lon[0]), math.degrees(ret_lat_lon[1]))
