from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^reconstruction_tree_map',views.reconstruction_tree_map, name='reconstruction_tree_map')
]

