from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt, csrf_protect

from utils.get_model import get_reconstruction_model_dict
from utils.wrapping_tools import wrap_reconstructed_polygons

import sys, json

import pygplates
import numpy as np

MODEL_DEFAULT = 'SETON2012'

MODEL_STORE = '/Users/Simon/GIT/gplates-web/MODELS/'


# Create your views here.
def index(request):
    return render_to_response(
        'list.html',
        context_instance = RequestContext(request,
            {}))

class PrettyFloat(float):
    def __repr__(self):
        return '%.2f' % self

def pretty_floats(obj):
    if isinstance(obj, float):
        return PrettyFloat(obj)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_floats, obj)             
    return obj

@csrf_exempt
def test_post(request):
    if not request.method == "POST":
        return HttpResponseBadRequest('expecting post requests!')
    else:
        #print request.POST
        data = json.loads(request.body)
        print data["geometry"]
        #for chunk in request.FILES['file'].chunks():
        #    data.append(chunk)
        #    #print chunk
        
        #print data
        return HttpResponse("OK")


