from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get_model_layer/?$',views.get_model_layer, name='get_model_layer'),
]

