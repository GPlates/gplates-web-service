from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^reconstruct_points/?$',views.reconstruct_points, name='reconstruct_points'),
    re_path(r'^reconstruct_feature_collection/?$',views.reconstruct_feature_collection, name='reconstruct_feature_collection'),
    re_path(r'^reconstruct_files/?$',views.reconstruct_files, name='reconstruct_files'),
    re_path(r'^coastlines/?$',views.get_coastline_polygons, name='coastlines'),
    re_path(r'^static_polygons/?$',views.get_static_polygons, name='static_polygons'),
    re_path(r'^motion_path/?$',views.motion_path, name='motion_path'),
    re_path(r'^flowline/?$',views.flowline, name='flowline'),
    re_path(r'^coastlines_low/?$',views.get_coastline_polygons_low, name='coastlines_low'),
]

