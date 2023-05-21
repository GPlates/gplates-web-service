from django.urls import re_path

from . import api, views

urlpatterns = [
    re_path(r"^model_names/?$", api.list_model_names),
    re_path(r"^models/?$", api.list_models),
    re_path(r"^model_layers/?$", api.list_model_layers),
    re_path(r"^get_model_details/?$", api.get_model_details),
    re_path(r"^test_browsable_api/?$", views.TestBrowsableAPI.as_view()),
]
