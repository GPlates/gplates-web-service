from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^plate_polygons/?$',views.velocity_within_topological_boundaries, name='velocity_plate_polygons'),
    url(r'^static_polygons/?$',views.velocity_within_static_polygons, name='velocity_static_polygons'),
]

