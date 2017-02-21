from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^reconstruct_points/?$',views.reconstruct_points, name='reconstruct_points'),
    url(r'^reconstruct_feature_collection/?$',views.reconstruct_feature_collection, name='reconstruct_feature_collection'),
    url(r'^coastlines/?$',views.get_coastline_polygons, name='coastlines'),
    url(r'^static_polygons/?$',views.get_static_polygons, name='static_polygons'),
    url(r'^motion_path/?$',views.motion_path, name='motion_path'),
    url(r'^flowline/?$',views.flowline, name='flowline'),
    url(r'^coastlines_low/?$',views.get_coastline_polygons_low, name='coastlines_low'),
]

