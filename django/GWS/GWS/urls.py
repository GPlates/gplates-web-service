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
from django.urls import include, re_path
from django.contrib import admin

from doc import views as doc_views

urlpatterns = [
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
    re_path(r"^list/", include("info.urls")),
    re_path(r"^map/", include("paleomap.urls")),
    re_path(r"^model/", include("model.urls")),
    re_path(r"^raster/", include("raster.urls")),
]
