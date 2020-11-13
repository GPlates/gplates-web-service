from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import (HttpResponse, 
    HttpResponseRedirect, HttpResponseBadRequest, 
    HttpResponseServerError, HttpResponseNotAllowed,
    JsonResponse)
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from utils.get_model import *

import sys, json, os
import xml.etree.ElementTree as ET

def list_model_names(request):
    response =  HttpResponse(
            json.dumps(get_model_name_list(settings.MODEL_STORE_DIR)), 
            content_type='application/json')
    
    response['Access-Control-Allow-Origin'] = '*'
    return response

def list_models(request):
    ret = []
    namespaces = {'dc': 'http://purl.org/dc/elements/1.1/'}
    for name in get_model_name_list(settings.MODEL_STORE_DIR,include_hidden=False):
        print(name)
        meta_file = settings.MODEL_STORE_DIR +'/'+name+'/'+name+'_metadata.xml'
        if os.path.isfile(meta_file):
            with open(meta_file, 'r', encoding="utf-8") as fp:
                data = fp.read()
                root = ET.fromstring(data)
                title = root.find('dc:title', namespaces)
                desc = root.find('dc:description', namespaces)
                tmp = {}
                tmp['name'] = name
                tmp['title'] = title.text
                tmp['desc'] = desc.text
                ret.append(tmp)
    response = HttpResponse(
            json.dumps(ret),
            content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response

def list_model_layers(request):
    model_name = request.GET.get('model',settings.MODEL_DEFAULT)
    response =  JsonResponse(
            get_reconstruction_model_dict(model_name))

    response['Access-Control-Allow-Origin'] = '*'
    return response 
