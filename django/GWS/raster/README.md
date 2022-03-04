## PostGIS Database and docker network

### Run in testing env

Start the database(on host computer): ``docker run --rm -it --name gws-postgis -e POSTGRES_PASSWORD=mysecretpassword  -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main -p 5432:5432 gplates/postgis``

Test the database(on host computer): `psql -d gplates -h localhost -U gplates`

### Run in production env

``docker run --restart always --name gws-postgis -e POSTGRES_PASSWORD=mysecretpassword -d -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main gplates/postgis``

### Log into the running container

`docker exec -ti gws-postgis /bin/bash`

### Create the sql file from a raster

`raster2pgsql -s 4326 -I -C -M Seton_etal_2020_PresentDay_AgeGrid.nc -F -t 100x100 public.age_grid > age_grid.sql`

### Import the sql file into DB

`psql -d gplates -f age_grid.sql`

### Keep the database data on host computer

- **Step 1**: mount the host folder with `-v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main`

- **Step 2**: If the database data folder is empty, you need to call initdb on the folder first.

`/usr/lib/postgresql/12/bin/initdb -D /var/lib/postgresql/data`

- **Step 3**: You also need to log into the container, `su postgres` and run `cd /workspace/ && ./init-db.sh`

- **Step 4**: import rasters with `psql -d gplates -f age_grid.sql`

### Use user-defined docker network

- `docker network create --driver bridge gws-net` (bridge is the default docker network)
- Use `--network gws-net` parameter to start docker containers
- In GWS server container, use `psql -d gplates -h gws-postgis -U gplates` to test DB


Note: Add `postgis.gdal_enabled_drivers = 'ENABLE_ALL'` in postgres.conf to enable all GDAL driver(useful when export images from raster table)

Note: Use `http://localhost:18000/raster/query?lon=99.50&lat=-40.24&raster_name=age_grid_geek_2007` to test raster table
