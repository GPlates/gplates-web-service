from django.urls import re_path

from . import api, finite_rotation, r12n_tree, views

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
    re_path(
        r"^get_rotation_map/?$",
        api.get_rotation_map,
        name="get_rotation_map",
    ),
    re_path(
        r"^get_reconstruction_tree_edges/?$",
        r12n_tree.get_reconstruction_tree_edges,
        name="get_reconstruction_tree_edges",
    ),
    re_path(
        r"^get_reconstruction_tree_height/?$",
        r12n_tree.get_reconstruction_tree_height,
        name="get_reconstruction_tree_height",
    ),
    re_path(
        r"^get_reconstruction_tree_leaves/?$",
        r12n_tree.get_reconstruction_tree_leaves,
        name="get_reconstruction_tree_leaves",
    ),
    re_path(
        r"^get_ancestors_in_reconstruction_tree/?$",
        r12n_tree.get_ancestors_in_reconstruction_tree,
        name="get_ancestors_in_reconstruction_tree",
    ),
    re_path(
        r"^get_reconstruction_tree/?$",
        r12n_tree.get_reconstruction_tree,
        name="get_reconstruction_tree",
    ),
]
