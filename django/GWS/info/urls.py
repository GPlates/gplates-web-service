from django.urls import re_path

from . import r_model

urlpatterns = [
    re_path(r'^model_names/?$', r_model.list_model_names),
    re_path(r'^models/?$', r_model.list_models),
    re_path(r'^model_layers/?$',r_model.list_model_layers)
]

