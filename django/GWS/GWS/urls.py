from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from .index import index
from .version import API_MAJOR, VERSION, get_version

# The public API. Served twice: unversioned from the root (/reconstruct/...)
# and under this release's major version (/v1/reconstruct/...). Both run the
# same code, so the /vN/ prefix changes nothing except making the version
# explicit. See the "API versioning" docs page and GitHub issue #24.
api_patterns = [
    path(
        "openapi",
        get_schema_view(
            title="GPlates Web Service API",
            description="the API allows users to access pyGPlates functionalities over network interface",
            version=VERSION,
        ),
        name="openapi-schema",
    ),
    path(
        "swagger-ui/",
        TemplateView.as_view(
            template_name="swagger-ui.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
    path(
        "version/",
        get_version,
        name="get_version",
    ),
    re_path(r"^reconstruct/", include("reconstruct.urls")),
    re_path(r"^topology/", include("topology.urls")),
    re_path(r"^velocity/", include("velocity.urls")),
    re_path(r"^rotation/", include("rotation.urls")),
    re_path(r"^mobile/", include("mobile.urls")),
    re_path(r"^earth/", include("earth.urls")),
    re_path(r"^model/", include("plate_model.urls")),
    re_path(r"^map/", include("paleomap.urls")),
    re_path(r"^raster/", include("raster.urls")),
]

urlpatterns = [
    re_path(r"^$", index),
    # admin stays unversioned: it is not part of the public API
    re_path(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    re_path(r"^admin/", admin.site.urls),
    # versioned alias, e.g. /v1/reconstruct/... (namespaced so URL names
    # such as "openapi-schema" still reverse to the unversioned path)
    re_path(rf"^{API_MAJOR}/", include((api_patterns, API_MAJOR))),
] + api_patterns
