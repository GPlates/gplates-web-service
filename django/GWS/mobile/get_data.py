import json
import os

from django.http import HttpResponse

script_path = os.path.dirname(os.path.realpath(__file__))

#
# get_scotese_etal_2021_global_temp
#
def get_scotese_etal_2021_global_temp(reqeust):
    data = load_csv_data(f"{script_path}/data/scotese_etal_2021_global_temp_1my.txt")
    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response


#
#
def get_graphs(request):
    with open(f"{script_path}/data/graphs.json", "r") as f:
        response = HttpResponse(f, content_type="application/json; charset=utf8")
        response["Access-Control-Allow-Origin"] = "*"
        return response


#
#
def get_cities(request):
    with open(f"{script_path}/data/cities.json", "r") as f:
        response = HttpResponse(f, content_type="application/json; charset=utf8")
        response["Access-Control-Allow-Origin"] = "*"
        return response


#
# get_scotese_etal_2021_global_temp
#
def get_scotese_etal_2021_deep_ocean_temp(reqeust):
    data = load_csv_data(f"{script_path}/data/deep-ocean-temp-Scotese-2021.txt")
    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response


def load_csv_data(filepath):
    data = {}
    with open(filepath, "r") as file:
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
