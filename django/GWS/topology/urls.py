from django.urls import re_path

from .subduction import get_subduction_zones
from .views import get_plate_polygons, get_topological_boundaries

urlpatterns = [
    re_path(
        r"^plate_boundaries/?$",
        get_topological_boundaries,
        name="plate_boundaries",
    ),
    re_path(r"^plate_polygons/?$", get_plate_polygons, name="plate_polygons"),
    re_path(
        r"^get_subduction_zones/?$", get_subduction_zones, name="get_subduction_zones"
    ),
]
