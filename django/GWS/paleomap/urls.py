from django.urls import re_path

from . import api

urlpatterns = [
    re_path(r'^get_cached_map$', api.overlay_cached_layers),
]
