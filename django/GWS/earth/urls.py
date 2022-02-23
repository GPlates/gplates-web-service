from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^litho1/?$',views.litho1, name='litho1'),
    re_path(r'^paleolithology/?$',views.paleolithology, name='paleolithology'),
    re_path(r'^paleomagnetism/?$',views.paleomagnetic_poles, name='paleomagnetism'),
]

