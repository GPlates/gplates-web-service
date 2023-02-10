"""GWS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, re_path, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from doc import views as doc_views

urlpatterns = [
    path(
        "openapi",
        get_schema_view(
            title="GPlates Web API",
            description="the API allows users to access pygplates functionalities over Internet",
            version="1.0.0",
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
    re_path(r"^$", doc_views.index),
    re_path(r"^examples/?$", doc_views.examples),
    re_path(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^reconstruct/", include("reconstruct.urls")),
    re_path(r"^topology/", include("topology.urls")),
    re_path(r"^velocity/", include("velocity.urls")),
    re_path(r"^rotation/", include("rotation.urls")),
    re_path(r"^mobile/", include("mobile.urls")),
    re_path(r"^earth/", include("earth.urls")),
    path("info/", include("info.urls")),
    re_path(r"^map/", include("paleomap.urls")),
    re_path(r"^model/", include("model.urls")),
    re_path(r"^raster/", include("raster.urls")),
]
