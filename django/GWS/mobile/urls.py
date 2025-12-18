from django.urls import re_path

from . import get_basemap_cfg, get_data, get_vector_layers

urlpatterns = [
    re_path(r"^get_basemaps/?$", get_basemap_cfg.get_basemaps, name="get_basemaps"),
    re_path(r"^get_rasters/?$", get_basemap_cfg.get_basemaps, name="get_rasters"),
    re_path(
        r"^get_vector_layers/?$", get_vector_layers.get_layers, name="get_vector_layers"
    ),
    re_path(
        r"^get_scotese_etal_2021_global_temp/?$",
        get_data.get_scotese_etal_2021_global_temp,
        name="get_scotese_etal_2021_global_temp",
    ),
    re_path(
        r"^get_scotese_etal_2021_deep_ocean_temp/?$",
        get_data.get_scotese_etal_2021_deep_ocean_temp,
        name="get_scotese_etal_2021_deep_ocean_temp",
    ),
    re_path(
        r"^get_graphs/?$",
        get_data.get_graphs,
        name="get_graphs",
    ),
    re_path(
        r"^get_datasets_info/?$",
        get_data.get_datasets_info,
        name="get_datasets_info",
    ),
    re_path(
        r"^get_cities/?$",
        get_data.get_cities,
        name="mobile_app_get_cities",
    ),
]
