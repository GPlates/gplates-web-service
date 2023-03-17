from django.urls import re_path

from . import api

urlpatterns = [
    re_path(r'^query/?$', api.query, name='query_raster'),
]
