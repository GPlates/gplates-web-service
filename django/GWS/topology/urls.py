from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r"^plate_boundaries/?$",
        views.get_topological_boundaries,
        name="plate_boundaries",
    ),
    re_path(r"^plate_polygons/?$", views.get_plate_polygons, name="plate_polygons"),
]
