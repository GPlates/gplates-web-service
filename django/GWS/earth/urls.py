from django.urls import re_path

from . import api, views
from .cities import get_cities, get_present_day_cities
from .labels import get_labels
from .plate_names import get_plate_names

urlpatterns = [
    re_path(r"^get_globe_mesh/?$", api.get_globe_mesh, name="get_globe_mesh"),
    re_path(
        r"^find_axis_and_angle/?$", api.find_axis_and_angle, name="find_axis_and_angle"
    ),
    re_path(
        r"^interp_two_locations/?$",
        api.interp_two_locations,
        name="interp_two_locations",
    ),
    re_path(r"^distance/?$", api.distance, name="distance"),
    re_path(r"^litho1/?$", views.litho1, name="litho1"),
    re_path(r"^paleolithology/?$", views.paleolithology, name="paleolithology"),
    re_path(r"^paleomagnetism/?$", views.paleomagnetic_poles, name="paleomagnetism"),
    re_path(r"^get_labels/?$", get_labels, name="get_labels"),
    re_path(r"^get_plate_names/?$", get_plate_names, name="get_plate_names"),
    re_path(
        r"^get_cities/?$",
        get_cities,
        name="get_cities",
    ),
    re_path(
        r"^get_present_day_cities/?$",
        get_present_day_cities,
        name="get_present_day_cities",
    ),
]
