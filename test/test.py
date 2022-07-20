import json
import os

import requests
import urllib3

urllib3.disable_warnings()

SERVER_URL = os.getenv("GWS_SERVER_URL")
if not SERVER_URL:
    SERVER_URL = "http://127.0.0.1:18000"
    print(f"Using server URL in script {SERVER_URL}")
else:
    print(f"Using server URL in environment variable {SERVER_URL}")

proxies = {"http": ""}

data = {"points": "95,54,142,-33", "time": 140}
r = requests.get(
    SERVER_URL + "/reconstruct/reconstruct_points/",
    params=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    print(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))

r = requests.post(
    SERVER_URL + "/reconstruct/reconstruct_points/",
    data=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    print(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
else:
    raise Exception(
        "FAILED: " + r.request.url + r.request.body + str(r.request.headers)
    )

data = {"points": "95,54,-117.26,32.7,142,-33", "time": 140, "fc": ""}
r = requests.post(
    SERVER_URL + "/reconstruct/reconstruct_points/",
    data=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    print(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
else:
    raise Exception(
        "FAILED: " + r.request.url + r.request.body + str(r.request.headers)
    )

r = requests.get(
    SERVER_URL + "/reconstruct/reconstruct_points/",
    params=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    print(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))

# raster query
data = {"lon": -70, "lat": 34, "raster_name": "age_grid_geek_2007"}
r = requests.get(
    SERVER_URL + "/raster/query/", params=data, verify=False, proxies=proxies
)
if r.status_code == 200:
    print(r.text)
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))

print("****************************")
print("All tests have passed!!!")
print("****************************")
