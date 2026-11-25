from django.http import HttpResponseBadRequest
from utils.decorators import return_HttpResponse

from .version_info import API_MAJOR, VERSION  # noqa: F401  (re-exported)


@return_HttpResponse()
def get_version(request):
    if request.method != "GET":
        return HttpResponseBadRequest(
            "Only HTTP GET request is supported for this endpoint."
        )
    return VERSION
