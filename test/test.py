import json
import logging
import os
import time

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


def test_reconstruct_points_get():
    '''test GET reconstructing points'''
    data = {"points": "95,54,142,-33", "time": 140}
    r = requests.get(
        SERVER_URL + "/reconstruct/reconstruct_points/",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! GET reconstruct points")
    else:
        raise Exception("FAILED: " + r.request.url + str(r.request.headers))


def test_reconstruct_points_post():
    '''test POST reconstructing points'''
    data = {"points": "95,54,142,-33", "time": 140}
    r = requests.post(
        SERVER_URL + "/reconstruct/reconstruct_points/",
        data=data,
        verify=False,
        proxies=proxies,
    )
    print(r.content)
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! POST reconstruct points")
    else:
        raise Exception(
            "FAILED: " + r.request.url +
            r.request.body + str(r.request.headers)
        )


def test_reconstruct_points_post_fc():
    '''
    test POST reconstructing points(return feature collection)
    '''
    data = {"points": "95,54,-117.26,32.7,142,-33", "time": 140, "fc": ""}
    r = requests.post(
        SERVER_URL + "/reconstruct/reconstruct_points/",
        data=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! POST reconstruct points(return feature collection)")
    else:
        raise Exception(
            "FAILED: " + r.request.url +
            r.request.body + str(r.request.headers)
        )


def test_reconstruct_points_get_fc():
    '''
    test GET reconstructing points(return feature collection)
    '''
    data = {"points": "95,54,-117.26,32.7,142,-33", "time": 140, "fc": ""}
    r = requests.get(
        SERVER_URL + "/reconstruct/reconstruct_points/",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
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


def test_reconstruct_feature_collection():
    '''
    test reconstruct feature collection
    '''

    data = {"feature_collection": json.dumps(fc), "time": 140}
    r = requests.get(
        SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! test reconstruct feature collection")
    else:
        raise Exception("FAILED: " + r.request.url + str(r.request.headers))


def test_assign_plate_ids():
    '''
    test assign plate ids for points
    '''
    data = {"points": "-10,50,-30,-70,0,0"}
    r = requests.get(
        SERVER_URL + "/reconstruct/assign_points_plate_ids",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! test assign plate ids for points")
    else:
        raise Exception("FAILED: " + r.request.url + str(r.request.headers))


def test_assign_plate_ids_geojson():
    '''
    test assign plate ids for geojson data
    '''
    data = {"feature_collection": json.dumps(fc)}
    r = requests.get(
        SERVER_URL + "/reconstruct/assign_geojson_plate_ids",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! test assign plate ids for geojson data")
    else:
        raise Exception("FAILED: " + r.request.url + str(r.request.headers))


def test_motion_path():
    '''
    test motion path
    '''
    data = {"seedpoints": "0,0", "movplate": 701}
    r = requests.get(
        SERVER_URL + "/reconstruct/motion_path",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! test motion path")
    else:
        raise Exception("FAILED: " + r.request.url + str(r.request.headers))


def test_rotate():
    '''
    test rotate
    '''
    data = {"point": "120,45", "axis": "20,-45", "angle": 20}
    r = requests.get(
        SERVER_URL + "/rotation/rotate",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! test rotate")
    else:
        raise Exception("FAILED: " + r.request.url + str(r.request.headers))


def test_find_axis_and_angle():
    '''
    test find_axis_and_angle
    '''
    data = {"point_a": "120,45", "point_b": "20,-45"}
    r = requests.get(
        SERVER_URL + "/earth/find_axis_and_angle",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! test find_axis_and_angle")
    else:
        raise Exception("FAILED: " + r.request.url + str(r.request.headers))


def test_interp_two_locations():
    '''
    test interp_two_locations
    '''
    data = {"point_a": "120,45", "point_b": "20,-45", "num": 10}
    r = requests.get(
        SERVER_URL + "/earth/interp_two_locations",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! test interp_two_locations")
    else:
        raise Exception("FAILED: " + r.request.url + str(r.request.headers))


def test_distance():
    '''
    test distance
    '''
    data = {"point_a": "120,45", "point_b": "20,-45"}
    r = requests.get(
        SERVER_URL + "/earth/distance",
        params=data,
        verify=False,
        proxies=proxies,
    )
    if r.status_code == 200:
        logging.info(json.dumps(json.loads(
            str(r.text)), sort_keys=True, indent=4))
        print("PASSED! test distance")
    else:
        raise Exception("FAILED: " + r.request.url + str(r.request.headers))


if __name__ == '__main__':
    test_reconstruct_points_get()
    time.sleep(1)
    test_reconstruct_points_post()
    time.sleep(1)
    test_reconstruct_points_get_fc()
    time.sleep(1)
    test_reconstruct_points_post_fc()
    time.sleep(1)
    test_reconstruct_feature_collection()
    time.sleep(1)
    test_assign_plate_ids()
    time.sleep(1)
    test_assign_plate_ids_geojson()
    time.sleep(1)
    test_motion_path()
    time.sleep(1)
    test_rotate()
    time.sleep(1)
    test_find_axis_and_angle()
    time.sleep(1)
    test_interp_two_locations()
    time.sleep(1)
    test_distance()

    print("****************************")
    print("All tests have passed!!!")
    print("****************************")
