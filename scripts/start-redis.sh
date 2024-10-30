#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
echo "$BASEDIR"
cd $BASEDIR  
docker compose -f ../docker/docker-compose-external-volumes.yml run --rm --service-ports gplates-redis
