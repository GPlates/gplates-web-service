from django.urls import re_path

from . import api

urlpatterns = [
    re_path(r'^query/?$', api.query, name='query_raster'),
    re_path(r'^query_m/?$', api.query_multiple_points,
            name='query_multiple_points'),

]
