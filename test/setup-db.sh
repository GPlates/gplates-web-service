#!/usr/bin/env bash

export PGPASSWORD=zaq12wsx

psql -d gplates -U gplates -h localhost -c "create schema raster;"
psql -d gplates -U gplates -h localhost < /tmp/crustal_thickness.sql