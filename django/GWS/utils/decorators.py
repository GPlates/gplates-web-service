import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from utils.parameter_helper import get_float, get_value_list
from utils.plate_model_utils import get_valid_time, is_time_valid_for_model

logger = logging.getLogger("default")


def check_get_post_request_and_get_params(func_pointer):
    """decorator to check request type"""

    def wrapped_func(*args, **kwargs):
        logger.debug("check_get_post_request_and_get_params decorator")
        if args[0].method == "POST":
            params = args[0].POST
        elif args[0].method == "GET":
            params = args[0].GET
        else:
            return HttpResponseBadRequest(
                "Unsupported request type. Only accept POST and GET requests."
            )

        kwargs["params"] = params
        return func_pointer(*args, **kwargs)

    return wrapped_func


def return_HttpResponse(content_type: str = "application/json"):
    """decorator to return HttpResponse.  "application/json" by default"""

    def inner(func_pointer):

        def wrapped_func(*args, **kwargs):
            logger.debug("return_HttpResponse decorator")
            ret = func_pointer(*args, **kwargs)

            if not isinstance(ret, str):
                return ret

            # add header for CORS
            # http://www.html5rocks.com/en/tutorials/cors/
            response = HttpResponse(ret, content_type=content_type)

            # TODO:
            # The "*" makes the service wide open to anyone. We should implement access control when time comes.
            response["Access-Control-Allow-Origin"] = "*"
            return response

        return wrapped_func

    return inner


def get_reconstruction_times(func_pointer):
    """decorator to get reconstruction times parameter"""

    def wrapped_func(*args, **kwargs):
        logger.debug("get_reconstruction_times decorator")
        params = kwargs["params"]
        times = get_value_list(params, "times", float)
        timef = get_float(params, "time", None)

        if timef is not None and len(times) > 0:
            return HttpResponseBadRequest(
                "The parameter 'time' and 'times' are mutually exclusive. Only one of them is allowed. "
            )

        if timef is None and len(times) == 0:
            return HttpResponseBadRequest(
                f"The parameters 'time' and 'times' are mutually exclusive and required. One and only one of the two parameters must present."
            )

        if len(times) == 0 and timef is not None:
            times.append(timef)

        model_name = params.get("model", settings.MODEL_DEFAULT)
        for t in times:
            if not is_time_valid_for_model(model_name, t):
                return HttpResponseBadRequest(
                    f"The time ({t}) is out of the scope of the reconstruction model {model_name} {get_valid_time(model_name)}."
                )

        kwargs["times"] = times
        return func_pointer(*args, **kwargs)

    return wrapped_func
