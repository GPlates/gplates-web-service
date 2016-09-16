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
from django.conf.urls import include, url
from django.contrib import admin

from doc import views as doc_views

urlpatterns = [
    url(r'^$', doc_views.index),
    url(r'^admin/', admin.site.urls),
    url(r'^reconstruct/', include('reconstruct.urls')),
    url(r'^topology/', include('topology.urls')),
    url(r'^rotation/', include('rotation.urls')),
    url(r'^reconstruct_file/', include('reconstruct_file.urls')),
]
