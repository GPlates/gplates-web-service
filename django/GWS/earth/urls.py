from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^litho1/?$',views.litho1, name='litho1'),
    url(r'^paleolithology/?$',views.paleolithology, name='paleolithology'),
    url(r'^paleomagnetism/?$',views.paleomagnetic_poles, name='paleomagnetism'),
]

