import json
import logging
import os

import requests
import urllib3

logging.basicConfig(filename="test.log", level=logging.INFO)

urllib3.disable_warnings()

SERVER_URL = os.getenv("GWS_SERVER_URL")
if not SERVER_URL:
    SERVER_URL = "http://127.0.0.1:18000"
    print(f"Using server URL in script {SERVER_URL}")
else:
    print(f"Using server URL in environment variable {SERVER_URL}")

proxies = {"http": ""}

# test GET reconstructing points
data = {"points": "95,54,142,-33", "time": 140}
r = requests.get(
    SERVER_URL + "/reconstruct/reconstruct_points/",
    params=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
    print("PASSED! GET reconstruct points")
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))

# test POST reconstructing points
r = requests.post(
    SERVER_URL + "/reconstruct/reconstruct_points/",
    data=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
    print("PASSED! POST reconstruct points")
else:
    raise Exception(
        "FAILED: " + r.request.url + r.request.body + str(r.request.headers)
    )

# test POST reconstructing points(return feature collection)
data = {"points": "95,54,-117.26,32.7,142,-33", "time": 140, "fc": ""}
r = requests.post(
    SERVER_URL + "/reconstruct/reconstruct_points/",
    data=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
    print("PASSED! POST reconstruct points(return feature collection)")
else:
    raise Exception(
        "FAILED: " + r.request.url + r.request.body + str(r.request.headers)
    )

# test GET reconstructing points(return feature collection)
r = requests.get(
    SERVER_URL + "/reconstruct/reconstruct_points/",
    params=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
    print("PASSED! GET reconstruct points(return feature collection)")
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))

# test raster query
data = {"lon": 99.50, "lat": -40.24, "raster_name": "age_grid_geek_2007"}
r = requests.get(
    SERVER_URL + "/raster/query/", params=data, verify=False, proxies=proxies
)
if r.status_code == 200:
    logging.info(r.text)
    print(f"PASSED! raster query ({r.text})")
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))


# test reconstruct feature collection
fc = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [128, -17],
                        [133, -18],
                        [138, -19],
                        [140, -23],
                        [139, -27],
                        [130, -27],
                        [128, -24],
                        [127, -21],
                        [127, -17],
                        [128, -17],
                    ]
                ],
            },
            "properties": {},
        }
    ],
}
data = {"feature_collection": json.dumps(fc), "time": 140}
r = requests.get(
    SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
    params=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
    print("PASSED! test reconstruct feature collection")
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))


# test assign plate ids for points
data = {"points": "-10,50,-30,-70,0,0"}
r = requests.get(
    SERVER_URL + "/reconstruct/assign_points_plate_ids",
    params=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
    print("PASSED! test assign plate ids for points")
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))


# test assign plate ids for geojson data
data = {"feature_collection": json.dumps(fc)}
r = requests.get(
    SERVER_URL + "/reconstruct/assign_geojson_plate_ids",
    params=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
    print("PASSED! test assign plate ids for geojson data")
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))


# test motion path
data = {"seedpoints": "0,0", "movplate": 701}
r = requests.get(
    SERVER_URL + "/reconstruct/motion_path",
    params=data,
    verify=False,
    proxies=proxies,
)
if r.status_code == 200:
    logging.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
    print("PASSED! test motion path")
else:
    raise Exception("FAILED: " + r.request.url + str(r.request.headers))

print("****************************")
print("All tests have passed!!!")
print("****************************")
