VERSION = "v1.0.0"
from utils.decorators import check_get_post_request_and_get_params, return_HttpResponse


@check_get_post_request_and_get_params
@return_HttpResponse()
def get_version(request, params={}):
    return VERSION
