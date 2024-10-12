#!/bin/bash

/etc/init.d/postgresql start

createdb gplates

psql -d gplates -f create-gws-db.sql

export PGPASSWORD=gplates
psql -d gplates -U gplates  -h localhost -f crustal_thickness.sql
psql -d gplates -U gplates  -h localhost -f gplates-db-restore.sql

/etc/init.d/postgresql stop
