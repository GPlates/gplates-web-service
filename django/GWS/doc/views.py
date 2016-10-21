from django.shortcuts import render
from django.template import RequestContext

# Create your views here.

def index(request):
    return render(
        request,
        'index.html',
        {}
    )

def examples(request):
    return render(
        request,
        'examples.html',
        {}
    )

