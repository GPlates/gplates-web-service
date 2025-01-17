import json
import os
import random

import requests

# The "requests" Python package is required to run this example https://pypi.org/project/requests/

SERVER_URL = os.getenv("GWS_SERVER_URL")
if not SERVER_URL:
    SERVER_URL = "https://gws.gplates.org"
    # SERVER_URL = "http://localhost:18000"
    print(f"Using server URL in script {SERVER_URL}")
else:
    print(f"Using server URL in environment variable {SERVER_URL}")

time = 100.0

# get all the plate IDs in the reconstruction tree at 100Ma
url = f"{SERVER_URL}/rotation/get_plate_ids?time={time}"
r = requests.get(url)
pids = json.loads(r.text)
# print(pids)

# pick up 10 random plate IDs from above plate IDs
random_pids = [pids[random.randint(0, len(pids) - 1)] for _ in range(10)]
print(random_pids)

times = list(range(0, 101, 10))  # give a list of times

# get quaternions for each time and plate ID
# if the plate id does not exist at the time, return identity rotation [1.0, 0.0, 0.0, 0.0](not moving)
url = f"{SERVER_URL}/rotation/get_quaternions?times={times}&pids={random_pids}"
# print(url)
r = requests.get(url)
ret = json.loads(r.text)
print(json.dumps(ret, indent=4, sort_keys=True))

# get euler pole and angle for each time and plate ID
# if the plate id does not exist at the time, return identity rotation [0.0, 90.0, 0.0](not moving)
# data format [lon, lat, angle]
url = f"{SERVER_URL}/rotation/get_euler_pole_and_angle?times={times}&pids={random_pids}"
# print(url)
r = requests.get(url)
ret = json.loads(r.text)
print(json.dumps(ret, indent=4, sort_keys=True))
