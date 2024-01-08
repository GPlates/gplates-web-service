import json
import logging

from django.conf import settings
from django.core.cache import caches
from django.http import HttpResponse, HttpResponseBadRequest
from utils.access_control import get_client_ip

logger = logging.getLogger("default")
access_logger = logging.getLogger("queue")

cache = caches["redis"]


def load_plate_names():
    """load plate names from file"""
    plate_names_dict = {}
    with open(
        f"{settings.EARTH_STORE_DIR}/Muller_etal_2019_plateID_list.csv", "rt"
    ) as csv_fp:
        for line in csv_fp:
            items = line.split(",")
            if len(items) < 3:
                logger.debug(f"invalid line: {line}")
                continue
            try:
                int(items[0])  # valid plate plate ID
            except (TypeError, ValueError) as ex:
                logger.debug(f"invalid plate ID: {line}")
                logger.debug(ex)
                continue
            plate_names_dict[items[0]] = [items[1].strip(), items[2].strip()]
    return plate_names_dict


cache.set("earth-plate-name-dict", load_plate_names())


def get_plate_names(request):
    """http://localhost:18000/earth/get_plate_names"""

    access_logger.info(get_client_ip(request) + f" {request.get_full_path()}")

    if request.method != "GET":
        return HttpResponseBadRequest("Only GET request is supported!")

    plate_names_dict = cache.get("earth-plate-name-dict")
    if plate_names_dict is None:
        logger.debug('Missed cache: cache.get("earth-plate-name-dict")')
        plate_names_dict = load_plate_names()
        cache.set("earth-plate-name-dict", plate_names_dict)

    response = HttpResponse(
        json.dumps(plate_names_dict),
        content_type="application/json",
    )

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
