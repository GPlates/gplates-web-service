#!/usr/bin/env bash

#
# 👀👉 This script is meant to be used in test.yml.
# 👀👉 If you would like to use it in other circumstances, make sure /tmp/crustal_thickness.sql exists.
#

export PGPASSWORD=gplates

psql -d gplates -U gplates -h localhost -c "create schema if not exists raster;"
psql -d gplates -U gplates -h localhost -c "create schema if not exists magnetic;"
psql -d gplates -U gplates -h localhost < /tmp/crustal_thickness.sql