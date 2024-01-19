from django.http import HttpResponse, HttpResponseBadRequest


def check_get_post_request_and_get_params(func_pointer):
    """decorator to check request type"""

    def wrapped_func(*args, **kwargs):
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
            ret = func_pointer(*args, **kwargs)

            # add header for CORS
            # http://www.html5rocks.com/en/tutorials/cors/
            response = HttpResponse(ret, content_type=content_type)

            # TODO:
            # The "*" makes the service wide open to anyone. We should implement access control when time comes.
            response["Access-Control-Allow-Origin"] = "*"
            return response

        return wrapped_func

    return inner
