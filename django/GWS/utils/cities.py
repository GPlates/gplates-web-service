import json
import logging

import pygplates
from django.conf import settings
from django.core.cache import caches
from utils.plate_model_utils import get_model_name_list
from utils.reconstruct_tools import assign_plate_ids

logger = logging.getLogger("default")
cache = caches["redis"]


def reload_cities():
    cache.delete("cities")
    return load_cities


def load_cities():
    try:
        with open(
            f"{settings.EARTH_STORE_DIR}/cities.json", "r", encoding="utf-8"
        ) as f:
            city_data = json.load(f)
            cities = []
            names = []
            city_pids = {}
            coords = []
            for city in city_data:
                logger.debug(city)
                names.append(city)
                coords.append(city_data[city])
                (lon, lat) = city_data[city]
                cities.append(pygplates.PointOnSphere(lat, lon))

            for model in get_model_name_list(settings.MODEL_REPO_DIR):
                pids_and_times = assign_plate_ids(cities, model)
                city_pids[model] = pids_and_times

            data = {"names": names, "coords": coords, "pids": city_pids}
            cache.add("cities", data)
            return data
    except OSError as err:
        logger.error(err)
        return None


def get_cities():
    cities = cache.get("cities")
    if cities is None:
        return load_cities()
    else:
        return cities


logger.info(get_cities())
