from django.urls import re_path

from . import get_data, get_raster_cfg, get_vector_layers

urlpatterns = [
    re_path(r"^get_rasters/?$", get_raster_cfg.get_rasters, name="get_rasters"),
    re_path(
        r"^get_vector_layers/?$", get_vector_layers.get_layers, name="get_vector_layers"
    ),
    re_path(
        r"^get_scotese_etal_2021_global_temp/?$",
        get_data.get_scotese_etal_2021_global_temp,
        name="get_scotese_etal_2021_global_temp",
    ),
    re_path(
        r"^get_graphs/?$",
        get_data.get_graphs,
        name="get_graphs",
    ),
    re_path(
        r"^get_cities/?$",
        get_data.get_cities,
        name="get_cities",
    ),
]
