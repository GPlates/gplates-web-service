from functools import wraps

from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import available_attrs
from django.conf import settings

import requests

def request_access(function=None, url=settings.ACCESS_CONTROL_URL):
    """
        the decorator to check access privilege
    """
    url = 'http://130.56.249.211:7777/access_control/request_access/'
    def request_access_decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def function_wrapper(request, *args, **kwargs):
            origin = request.META.get('HTTP_ORIGIN', None)

            if url: #access control has been enabled.
                apikey = None
                if request.method == 'GET':
                    apikey = request.GET.get('apikey', None)
                elif request.method == 'POST': 
                    apikey = request.POST.get('apikey', None)
                
                if not apikey:    
                    return HttpResponseForbidden()
    
                payload = {'path': request.path_info, 'key': apikey}

                if origin:
                    payload['origin'] = origin
 
                r = requests.get(url, params=payload)
    
                if r.status_code != 200:
                    return HttpResponseForbidden()
            
            response = func(request, *args, **kwargs)
            if origin:
                response['Access-Control-Allow-Origin'] = origin        
            return response

        return function_wrapper

    #in order to support both @request_access and @request_access()
    #@request_access equals request_access(someFunction)
    #@request_access() equals request_access()(someFunction)
    if function is None:
        return request_access_decorator
    else:
        return request_access_decorator(function)

