#!/bin/bash

echo $1

PORT=18007

if [ -z "$1" ]
then
  docker run -d --rm --name gplates_web_service_test -p $PORT:80 gplates/gws
else
  docker run -d --rm --name gplates_web_service_test -v $1:/gws -p $PORT:80  gplates/gws
fi

