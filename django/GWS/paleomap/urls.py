from django.urls import re_path

from . import apis

urlpatterns = [
    re_path(r'^get_cached_map$', apis.overlay_cached_layers),
]
