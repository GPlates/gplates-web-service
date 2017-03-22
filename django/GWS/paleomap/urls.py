from django.conf.urls import url

import views, animation

urlpatterns = [
    url(r'^$', views.create),
#    url(r'^animation/?$', animation.generate),
]

