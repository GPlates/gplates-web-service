import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from PIL import Image


def overlay_cached_layers(request):
    """
        return the overlay of prepared map layers
        http://localhost:18000/map/get_cached_map?layers=agegrid,coastlines,topologies&model=MATTHEWS2016_mantle_ref
    """
    time = request.GET.get('time', 140)
    model = request.GET.get('model', settings.MODEL_DEFAULT)
    layers_str = request.GET.get('layers', '')
    layers = layers_str.split(',')
    layers_path = f"{settings.BASE_DIR}/DATA/MODELS/{model}/map-layers/"

    if len(layers) == 0 or layers[0] == '':
        return HttpResponseBadRequest(f'Invalid request. No layers found. layers({layers_str})')

    print(f"{layers_path}/{layers[0]}/{layers[0]}-{time}-Ma.png")
    if not os.path.isfile(f"{layers_path}/{layers[0]}/{layers[0]}-{time}-Ma.png"):
        return HttpResponseBadRequest(f"Layer({layers[0]}) at {time}Ma not found in model({model}).")

    # read in the first layer
    imgdata = Image.open(
        f"{layers_path}/{layers[0]}/{layers[0]}-{time}-Ma.png")

    # now overlay the other layers
    if len(layers) > 1:
        for layer in layers[1:]:
            if not os.path.isfile(f"{layers_path}/{layer}/{layer}-{time}-Ma.png"):
                return HttpResponseBadRequest(f"Layer({layer}) at {time}Ma not found in model({model}).")

            overlay = Image.open(
                f"{layers_path}/{layer}/{layer}-{time}-Ma.png")
            imgdata.paste(overlay, (0, 0), mask=overlay)

    response = HttpResponse(content_type="image/png")
    imgdata.save(response, "PNG")
    response["Access-Control-Allow-Origin"] = "*"
    return response
