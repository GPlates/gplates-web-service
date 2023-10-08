from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r"^plate_polygons/?$",
        views.velocity_within_topological_boundaries,
        name="velocity_plate_polygons",
    ),
    re_path(
        r"^static_polygons/?$",
        views.velocity_within_static_polygons,
        name="velocity_static_polygons",
    ),
]
