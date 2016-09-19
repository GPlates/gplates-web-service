from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^test_post/',views.test_post, name='test_post'),
    url(r'^test_post_files/',views.test_post_files, name='test_post_files'),
    url(r'^html_model_list/',views.html_model_list, name='html_model_list'),
    url(r'^subduction/',views.subduction, name='subduction')
]

