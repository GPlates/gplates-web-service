import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from utils.access_control import get_client_ip

logger = logging.getLogger("default")
access_logger = logging.getLogger("queue")

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
            plate_id = int(items[0])
        except:
            logger.debug(f"invalid plate ID: {line}")
            continue
        plate_names_dict[str(plate_id)] = {"name": items[1], "desc": items[2]}


def get_plate_names(request):
    """http://localhost:18000/earth/get_plate_names"""
    access_logger.info(get_client_ip(request) + f" {request.get_full_path()}")
    if request.method != "GET":
        return HttpResponseBadRequest("Only GET request is supported!")

    response = HttpResponse(
        json.dumps(plate_names_dict),
        content_type="application/json",
    )

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
