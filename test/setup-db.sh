#!/usr/bin/env bash

export PGPASSWORD=gplates

psql -d gplates -U gplates -h localhost -c "create schema raster;"
psql -d gplates -U gplates -h localhost < /tmp/crustal_thickness.sql