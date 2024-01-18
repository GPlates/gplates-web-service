import json
import logging

import pygplates
import requests
from django.conf import settings
from django.core.cache import caches
from utils.plate_model_utils import (
    UnrecognizedModel,
    get_model_name_list,
    get_rotation_model,
    get_static_polygons,
)
from utils.round_float import round_floats

logger = logging.getLogger("default")
cache = caches["redis"]


def load_cities():
    try:
        city_data = {}
        with open(
            f"{settings.EARTH_STORE_DIR}/cities.json", "r", encoding="utf-8"
        ) as f:
            city_data = json.load(f)

            new_city_data["coords"] = {}
            coords_str = ""
            count = 0
            for city in city_data["coords"]:
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

            with open(
                f"{settings.EARTH_STORE_DIR}/cities.json", "w", encoding="utf-8"
            ) as f:
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
