#!/bin/bash

if [ ! -d "/gws/django/GWS/data/model-repo/" ] 
then
   pmm download all /gws/django/GWS/data/model-repo/
fi

service apache2 start

tail -f /var/log/apache2/error.log
