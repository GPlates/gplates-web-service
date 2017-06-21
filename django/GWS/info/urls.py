from django.conf.urls import url

import r_model

urlpatterns = [
    url(r'^model_names/?$', r_model.list_model_names),
    url(r'^models/?$', r_model.list_models),
    url(r'^model_layers/?$',r_model.list_model_layers)
]

