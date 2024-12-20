import json
import random

import requests

# The "requests" Python package is required to run this example https://pypi.org/project/requests/

SERVER_URL = "https://gws.gplates.org"

NUM = 5000  # number of locations

lons = [i / 100 for i in random.sample(range(-18000, 18000), NUM)]
lats = [i / 100 for i in random.sample(range(-9000, 9000), NUM)]

data = {"time": 10}
data["lons"] = str(lons)
data["lats"] = str(lats)
r = requests.post(
    SERVER_URL + "/reconstruct/reconstruct_points/", data=data, verify=True
)
print(r.text)

print(
    f"\nThe coordinates of {len(json.loads(r.text)['coordinates'])} locations have been returned.\n"
)
