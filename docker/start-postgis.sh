#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
echo "$BASEDIR"
cd $BASEDIR  
docker-compose run -f docker-compose-mc.yml --rm --service-ports gws-postgis