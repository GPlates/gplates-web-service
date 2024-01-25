#!/bin/bash

/etc/init.d/postgresql start

createdb gplates

psql -d gplates -f create-gws-db.sql

psql -d gplates -f crustal_thickness.sql
