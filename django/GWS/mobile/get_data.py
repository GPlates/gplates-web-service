import json
import os

from django.conf import settings
from django.http import HttpResponse

script_path = os.path.dirname(os.path.realpath(__file__))
data_path = f"{settings.BASE_DIR}/DATA/mobile-app/"

#
# get_scotese_etal_2021_global_temp
#


def get_scotese_etal_2021_global_temp(reqeust):
    data = load_csv_data(
        f"{data_path}/scotese_etal_2021_global_temp_1my.txt")
    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response


#
#
def get_graphs(request):
    with open(f"{data_path}/graphs.json", "r", encoding="utf-8") as f:
        response = HttpResponse(
            f, content_type="application/json; charset=utf8")
        response["Access-Control-Allow-Origin"] = "*"
        return response


#
#
def get_cities(request):
    with open(f"{data_path}/cities.json", "r", encoding="utf-8") as f:
        response = HttpResponse(
            f, content_type="application/json; charset=utf8")
        response["Access-Control-Allow-Origin"] = "*"
        return response


#
# get_scotese_etal_2021_global_temp
#
def get_scotese_etal_2021_deep_ocean_temp(reqeust):
    data = load_csv_data(
        f"{data_path}/deep-ocean-temp-Scotese-2021.txt")
    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response


def load_csv_data(filepath):
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
