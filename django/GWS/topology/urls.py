from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^plate_boundaries',views.get_topological_boundaries, name='plate_boundaries'),
    url(r'^plate_polygons',views.get_plate_polygons, name='plate_polygons')
]

