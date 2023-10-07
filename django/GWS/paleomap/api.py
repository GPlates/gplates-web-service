import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from PIL import Image
from plate_model_manager import PlateModel


def overlay_cached_layers(request):
    """This is experimental code to provide cached layer images
    return the overlay of prepared map layers
    http://localhost:18000/map/get_cached_map?layers=AgeGrids,Coastlines,Topologies&model=MATTHEWS2016_mantle_ref&bg=211,211,211&size=1116,558
    the layer image files need to follow the naming convention.
    If the "bg" parameter does not present, use transparent background
    """
    time = request.GET.get("time", 140)
    model = request.GET.get("model", settings.MODEL_DEFAULT)
    background_str = request.GET.get("bg", "0, 0, 0, 0")
    size_str = request.GET.get("size", "1116, 558")
    layers_str = request.GET.get("layers", "")
    layers = layers_str.split(",")

    plate_model = PlateModel(
        model.lower(), data_dir=settings.MODEL_REPO_DIR, readonly=True
    )

    layer_paths = []
    for layer in layers:
        try:
            layer_paths.append(plate_model.get_raster(layer, time))
        except Exception as e:
            print(e)
            continue

    if len(layer_paths) == 0:
        return HttpResponseBadRequest(
            f"Invalid request. No valid layer found. layers({layers_str})"
        )

    # determine the image size
    try:
        size = size_str.split(",")
        if len(size) == 2:
            size = tuple([int(i) for i in size])
        else:
            raise Exception("invalid size parameter.")
    except:
        size = (1116, 558)

    # determine the backgroud
    try:
        background = background_str.split(",")
        if len(background) == 3 or len(background) == 4:
            background = tuple([int(i) for i in background])
        else:
            raise Exception("invalid background parameter.")
    except:
        size = (0, 0, 0, 0)

    # create a background
    imgdata = Image.new("RGBA", size, background)

    # now overlay the other layers
    if len(layer_paths) > 0:
        for layer_path in layer_paths:
            if not os.path.isfile(layer_path):
                return HttpResponseBadRequest(
                    f"Layer({layer_path}) at {time}Ma not found in model({model})."
                )

            overlay = Image.open(layer_path).convert("RGBA")
            overlay.resize(size)
            imgdata.paste(overlay, (0, 0), mask=overlay)

    # return the image
    response = HttpResponse(content_type="image/png")
    imgdata.save(response, "PNG")
    response["Access-Control-Allow-Origin"] = "*"
    return response
