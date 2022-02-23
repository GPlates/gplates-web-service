from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^query/?$',views.query, name='query_raster'),
]

