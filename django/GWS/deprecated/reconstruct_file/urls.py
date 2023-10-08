from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^test_post/?$", views.test_post, name="test_post"),
    re_path(r"^test_post_files/?$", views.test_post_files, name="test_post_files"),
    re_path(r"^html_model_list/?$", views.html_model_list, name="html_model_list"),
    re_path(r"^subduction/?$", views.subduction, name="subduction"),
]
