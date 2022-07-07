#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
echo "$BASEDIR"
cd $BASEDIR  
docker-compose run --rm --service-ports gws-postgis