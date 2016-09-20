from django.shortcuts import render, render_to_response
from django.template import RequestContext

# Create your views here.

def index(request):
    return render_to_response(
        'index.html',
        context_instance = RequestContext(request,
            {}))

def examples(request):
    return render_to_response(
        'examples.html',
        context_instance = RequestContext(request,
            {}))

