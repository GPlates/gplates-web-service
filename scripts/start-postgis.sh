#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
echo "$BASEDIR"
cd $BASEDIR  
docker-compose -f docker-compose-mc.yml run  --rm --service-ports gws-postgis