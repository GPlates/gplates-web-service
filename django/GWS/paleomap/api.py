import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from PIL import Image


def overlay_cached_layers(request):
    """
        return the overlay of prepared map layers
        http://localhost:18000/map/get_cached_map?layers=agegrid,coastlines,topologies&model=MATTHEWS2016_mantle_ref&bg=211,211,211&size=1116,558
        the layer image files need to follow the naming convention.
        If the "bg" parameter does not present, use transparent background
    """
    time = request.GET.get('time', 140)
    model = request.GET.get('model', settings.MODEL_DEFAULT)
    background_str = request.GET.get('bg', '0, 0, 0, 0')
    size_str = request.GET.get('size', '1116, 558')
    layers_str = request.GET.get('layers', '')
    layers = layers_str.split(',')
    layers_path = f"{settings.BASE_DIR}/DATA/MODELS/{model}/map-layers/"

    if len(layers) == 0 or layers[0] == '':
        return HttpResponseBadRequest(f'Invalid request. No layers found. layers({layers_str})')

    # the layer image files need to follow the naming convention.
    print(f"{layers_path}/{layers[0]}/{layers[0]}-{time}-Ma.png")
    if not os.path.isfile(f"{layers_path}/{layers[0]}/{layers[0]}-{time}-Ma.png"):
        return HttpResponseBadRequest(f"Layer({layers[0]}) at {time}Ma not found in model({model}).")

    # determine the image size
    try:
        size = size_str.split(',')
        if len(size) == 2:
            size = tuple([int(i) for i in size])
        else:
            raise Exception('invalid size parameter.')
    except:
        size = (1116, 558)

    # determine the backgroud
    try:
        background = background_str.split(',')
        if len(background) == 3 or len(background) == 4:
            background = tuple([int(i) for i in background])
        else:
            raise Exception('invalid background parameter.')
    except:
        size = (0, 0, 0, 0)

    # create a background
    imgdata = Image.new('RGBA', size, background)

    # now overlay the other layers
    if len(layers) > 0:
        for layer in layers:
            if not os.path.isfile(f"{layers_path}/{layer}/{layer}-{time}-Ma.png"):
                return HttpResponseBadRequest(f"Layer({layer}) at {time}Ma not found in model({model}).")

            overlay = Image.open(
                f"{layers_path}/{layer}/{layer}-{time}-Ma.png").convert("RGBA")
            overlay.resize(size)
            imgdata.paste(overlay, (0, 0), mask=overlay)

    # return the image
    response = HttpResponse(content_type="image/png")
    imgdata.save(response, "PNG")
    response["Access-Control-Allow-Origin"] = "*"
    return response
