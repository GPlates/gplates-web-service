from django.http import HttpResponseBadRequest
from utils.decorators import return_HttpResponse

VERSION = "v1.0.0"


@return_HttpResponse()
def get_version(request):
    if request.method != "GET":
        return HttpResponseBadRequest(
            "Only HTTP GET request is supported for this endpoint."
        )
    return VERSION
