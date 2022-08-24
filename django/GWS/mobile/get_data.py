import json
import os

from django.http import HttpResponse

script_path = os.path.dirname(os.path.realpath(__file__))

#
# get_scotese_etal_2021_global_temp
#
def get_scotese_etal_2021_global_temp(reqeust):
    data = {}
    with open(f"{script_path}/scotese_etal_2021_global_temp_1my.txt", "r") as file:
        for line in file:
            parts = line.split()
            if (len(parts) != 2) or parts[0].startswith("#"):
                continue
            try:
                data[parts[0]] = float(parts[1])
            except:
                print(f"bad line {line}!")
                continue

    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response
