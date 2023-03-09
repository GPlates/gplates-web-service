from django.urls import re_path

from . import views, api

urlpatterns = [
    re_path(r'^find_axis_and_angle/?$', api.find_axis_and_angle,
            name='find_axis_and_angle'),
    re_path(r'^interp_two_locations/?$', api.interp_two_locations,
            name='interp_two_locations'),
    re_path(r'^distance/?$', api.distance,
            name='distance'),
    re_path(r'^litho1/?$', views.litho1, name='litho1'),
    re_path(r'^paleolithology/?$', views.paleolithology, name='paleolithology'),
    re_path(r'^paleomagnetism/?$', views.paleomagnetic_poles,
            name='paleomagnetism'),
]
