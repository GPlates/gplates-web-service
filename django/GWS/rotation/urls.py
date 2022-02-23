from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^reconstruction_tree_map/?$',views.reconstruction_tree_map, name='reconstruction_tree_map')
]

