from django.urls import re_path

from . import (
    get_polygons,
    reconstruct_files,
    reconstruct_points,
    views,
    reconstruct_feature_collection,
    assign_plate_id,
)

urlpatterns = [
    re_path(
        r"^reconstruct_points/?$",
        reconstruct_points.reconstruct,
        name="reconstruct_points",
    ),
    re_path(
        r"^reconstruct_feature_collection/?$",
        reconstruct_feature_collection.reconstruct,
        name="reconstruct_feature_collection",
    ),
    re_path(
        r"^reconstruct_files/?$",
        reconstruct_files.reconstruct,
        name="reconstruct_files",
    ),
    re_path(r"^coastlines/?$", get_polygons.get_coastline_polygons, name="coastlines"),
    re_path(
        r"^static_polygons/?$",
        get_polygons.get_static_polygons,
        name="static_polygons",
    ),
    re_path(r"^motion_path/?$", views.motion_path, name="motion_path"),
    re_path(r"^flowline/?$", views.flowline, name="flowline"),
    re_path(
        r"^coastlines_low/?$",
        get_polygons.get_coastline_polygons_low,
        name="coastlines_low",
    ),
    re_path(
        r"^assign_points_plate_ids/?$",
        assign_plate_id.get_points_pids,
        name="assign_points_plate_ids",
    ),
]
