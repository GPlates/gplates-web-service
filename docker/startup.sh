#!/bin/bash

if [ ! -d "/gws/django/GWS/data/model-repo/" ] 
then
   pmm download all /gws/django/GWS/data/model-repo/
fi

if [ ! -d "/gws/log/" ] 
then
   mkdir -p /gws/log
fi

chown www-data:www-data -R /gws/log

service apache2 start

tail -f /var/log/apache2/error.log
