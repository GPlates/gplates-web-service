from django.urls import re_path

from . import finite_rotation, views, api

urlpatterns = [
    re_path(
        r"^reconstruction_tree_map/?$",
        views.reconstruction_tree_map,
        name="reconstruction_tree_map",
    ),
    re_path(
        r"^get_euler_pole_and_angle/?$",
        finite_rotation.get_euler_pole_and_angle,
        name="get_euler_pole_and_angle",
    ),
    re_path(
        r"^get_quaternions/?$",
        finite_rotation.get_quaternions,
        name="get_quaternions",
    ),
    re_path(
        r"^get_plate_ids/?$",
        finite_rotation.get_plate_ids,
        name="get_plate_ids",
    ),
    re_path(
        r"^rotate/?$",
        api.rotate,
        name="rotate",
    ),
]
