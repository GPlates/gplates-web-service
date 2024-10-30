#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
echo "$BASEDIR"
cd $BASEDIR  
docker compose -f ../docker/docker-compose-code-and-db-volume.yml down