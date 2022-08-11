import os

from django.http import HttpResponse

script_path = os.path.dirname(os.path.realpath(__file__))

#
# get vector layers for a given model
#
def get_layers(request):
    model_name = request.GET.get("model", "SETON2012")
    with open(f"{script_path}/{model_name}-layers.json", "r") as f:
        response = HttpResponse(f, content_type="application/json; charset=utf8")
        response["Access-Control-Allow-Origin"] = "*"
        return response
