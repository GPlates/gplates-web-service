from django.urls import re_path

from . import get_raster_cfg

urlpatterns = [
    re_path(r"^get_rasters/?$", get_raster_cfg.get_rasters, name="get_rasters"),
]
