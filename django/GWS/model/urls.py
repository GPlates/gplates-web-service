from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^get_model_layer/?$',views.get_model_layer, name='get_model_layer'),
]

