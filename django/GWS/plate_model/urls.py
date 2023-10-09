from django.urls import re_path

from . import api, views

urlpatterns = [
    re_path(r"^list/?$", api.list_model_names),
    re_path(r"^list_layers/?$", api.list_model_layers),
    re_path(r"^show/?$", api.get_model_details),
    re_path(r"^test_browsable_api/?$", views.TestBrowsableAPI.as_view()),
]
