from django.urls import re_path

from . import get_raster_cfg, get_vector_layers

urlpatterns = [
    re_path(r"^get_rasters/?$", get_raster_cfg.get_rasters, name="get_rasters"),
    re_path(
        r"^get_vector_layers/?$", get_vector_layers.get_layers, name="get_vector_layers"
    ),
]
