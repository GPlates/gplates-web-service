from functools import wraps

from django.utils.decorators import available_attrs
from django.conf import settings

def request_access(function=None, url=settings.ACCESS_CONTROL_URL):
    """
        the decorator to check access privilege
    """
    def request_access_decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def function_wrapper(request, *args, **kwargs):
            return func(request, *args, **kwargs)
        return function_wrapper

    #in order to support both @request_access and @request_access()
    #@request_access equals request_access(someFunction)
    #@request_access() equals request_access()(someFunction)
    if function is None:
        return request_access_decorator
    else:
        return request_access_decorator(function)
