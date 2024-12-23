#!/bin/bash

# use ./scripts/start-single-gws-test.sh `pwd` to use the source code in the current working directory
# use ./scripts/start-single-gws-test.sh to use the built-in source code

echo $1

PORT=18007

if [ -z "$1" ]
then
  docker run -d --rm --name gplates_web_service_test -p $PORT:80 gplates/gws
else
  docker run -d --rm --name gplates_web_service_test -v $1:/gws -p $PORT:80  gplates/gws
fi

