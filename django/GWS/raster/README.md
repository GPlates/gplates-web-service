Run in testing env
``docker run --rm -it --name gws-postgis -e POSTGRES_PASSWORD=mysecretpassword -v`pwd`:/workspace -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main -p 5432:5432 gplates/postgis``

Run in production env
``docker run --restart always --name gws-postgis -e POSTGRES_PASSWORD=mysecretpassword -d -v`pwd`:/workspace -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main gplates/postgis``

Log into the running container
`docker exec -ti gws-postgis /bin/bash`


Create the sql file from a raster
`raster2pgsql -s 4326 -I -C -M Seton_etal_2020_PresentDay_AgeGrid.nc -F -t 100x100 public.age_grid > age_grid.sql`

Import the sql file into DB
`psql -d gplates -f age_grid.sql`

/usr/lib/postgresql/12/bin/initdb -D /var/lib/postgresql/data

add postgis.gdal_enabled_drivers = 'ENABLE_ALL' in postgres.conf