from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^reconstruct_points/',views.reconstruct_points, name='reconstruct_points'),
    url(r'^coastlines/',views.get_coastline_polygons, name='coastlines'),
    url(r'^static_polygons/',views.get_static_polygons, name='static_polygons')
]

