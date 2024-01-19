import json
import os

import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError

script_path = os.path.dirname(os.path.realpath(__file__))
data_path = f"{settings.MOBILE_APP_DIR}"


def get_scotese_etal_2021_global_temp(reqeust):
    """get_scotese_etal_2021_global_temp"""
    data = load_csv_data(f"{data_path}/scotese_etal_2021_global_temp_1my.txt")
    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_graphs(request):
    """"""
    with open(f"{data_path}/graphs.json", "r", encoding="utf-8") as f:
        response = HttpResponse(f, content_type="application/json; charset=utf8")
        response["Access-Control-Allow-Origin"] = "*"
        return response


def get_cities(request):
    """get the coordinates and PIDs of cities
    deprecated. only using in mobile app. will be replaced by https://gws.gplate.org/earth/get_cities",
    """
    try:
        city_data = {}
        with open(f"{data_path}/cities.json", "r", encoding="utf-8") as f:
            city_data = json.load(f)

        if city_data["dirty"]:
            new_city_data = {}
            new_city_data["dirty"] = False
            new_city_data["coords"] = {}
            coords_str = ""
            count = 0
            for city in city_data["coords"]:
                # print(city)
                lon = city_data["coords"][city][0]
                lat = city_data["coords"][city][1]
                coords_str += f"{lon},{lat},"
                new_city_data["coords"][city] = [lon, lat, count]
                count += 1

            url = f"https://gws.gplates.org/reconstruct/assign_points_plate_ids?points={coords_str[:-1]}"

            # get plate ids
            new_city_data["plate-ids"] = {}
            for model in city_data["plate-ids"]:
                ret = requests.get(f"{url}&model={model}")
                pids = json.loads(ret.content)
                new_city_data["plate-ids"][model] = pids

            new_city_data["standby"] = city_data["standby"]

            with open(f"{data_path}/cities.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(new_city_data, indent=4))

            response = HttpResponse(
                json.dumps(new_city_data), content_type="application/json; charset=utf8"
            )
        else:
            response = HttpResponse(
                json.dumps(city_data), content_type="application/json; charset=utf8"
            )

        response["Access-Control-Allow-Origin"] = "*"
        return response
    except OSError as err:
        print(err)
        return HttpResponseServerError("Unable to find the data of cities!")


def get_scotese_etal_2021_deep_ocean_temp(reqeust):
    """get_scotese_etal_2021_global_temp"""
    data = load_csv_data(f"{data_path}/deep-ocean-temp-Scotese-2021.txt")
    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response


def load_csv_data(filepath):
    """"""
    data = {}
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.split()
            if (len(parts) != 2) or parts[0].startswith("#"):
                continue
            try:
                data[parts[0]] = float(parts[1])
            except:
                print(f"bad line {line}!")
                continue
    return data
