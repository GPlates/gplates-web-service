## Quick start

If you would like to try the GPlates Web Service very quickly, use the commands in this "quick start" section. The commands will start the docker container using the built-in source code. And the PostGIS database is not available. See "PostGIS Database and docker network" section for database configuration.

#### 🟢 Run the service as daemon in the background

`docker run -d -p 80:80 --restart always gplates/gws`

Use the link below to verify the service is up and running.

http://localhost/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012

#### 🟢 Run the service interactively (you can check the error messages in the console)

`docker run --rm -it -p 8888:80 gplates/gws`

## Use docker container for development

- Create **gws-net** if haven't `docker network create --driver bridge gws-net`

- Go to the root directory of this repository and run `` docker run -it --rm -v `pwd`:/gws -p 18000:80 --network gws-net gplates/gws /bin/bash ``

- Go to folder "django/GWS/", run `copy env.template .env` and edit file ".env" according to the database configuration

- Start the database `docker run --rm -it --name gws-postgis -e POSTGRES_PASSWORD=mysecretpassword -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main -p 5432:5432 --network gws-net gplates/postgis`

- Inside the virtual machine: `cd /gws/django/GWS && python3 manage.py runserver 0.0.0.0:80`

- Test the dev server with url http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012.

**IMPORTANT: ⚠ Make sure the BEDUG is set to True in settings.py**

## Update the docker image

Go to the root directory of this repository and run

`docker build -f docker/Dockerfile -t gplates/gws .`

## Run docker container in production env

Go to folder "%{git-repo-root}/django/GWS/", run `copy env.template .env` and edit file ".env" according to the database configuration

Go to the repository root directory, such as `/var/www/gplates-web-service`, and run

`` docker run -d -v `pwd`:/gws -p 18000:80 --restart always gplates/gws ``

The server is running at http://your-ip-address:18000. You may need to do some http requests redirection work.

You can try "--network host" argument. The command below will start a server listening on the 80 port of the host computer.

If you start the docker container with "--network host", the localhost and 127.0.0.1 inside docker container are pointing to the host computer.

`` docker run -d -v `pwd`:/gws --network host --restart always gplates/gws ``

## PostGIS database and docker network

### Run PostGIS in testing env

Start the database(on host computer): `docker run --rm -it --name gws-postgis -e POSTGRES_PASSWORD=mysecretpassword -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main -p 5432:5432 --network gws-net gplates/postgis`

Test the database(on host computer): `psql -d gplates -h localhost -U gplates`

### Run PostGIS in production env

`docker run --restart always --name gws-postgis -e POSTGRES_PASSWORD=mysecretpassword -d -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main gplates/postgis`

### Log into the running container

`docker exec -ti gws-postgis /bin/bash`

### Create the sql file from a raster

`raster2pgsql -s 4326 -I -C -M Seton_etal_2020_PresentDay_AgeGrid.nc -F -t 100x100 public.age_grid > age_grid.sql`

### Import the sql file into DB

`psql -d gplates -f age_grid.sql`

### Keep the database data on host computer

- **Step 1**: mount the host folder with `-v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main`

- **Step 2**: If the database data folder is empty, you need to log into the docker container and call **initdb** on the folder first.

`/usr/lib/postgresql/12/bin/initdb -D /var/lib/postgresql/data`

- **Step 3**: You also need to log into the container, `su postgres` and run `cd /workspace/ && ./init-db.sh`

- **Step 4**: import rasters with `psql -d gplates -f age_grid.sql`

### Use user-defined docker network

- `docker network create --driver bridge gws-net` (bridge is the default docker network)
- Use `--network gws-net` parameter to start docker containers
- In GWS server container, use `psql -d gplates -h gws-postgis -U gplates` to test DB

## Docker compose

run postgis: `docker-compose run --rm --service-ports gws-postgis`

run gws for debug `docker-compose run --rm --service-ports gws /bin/bash`

create volume from local folder:

`docker volume create --name gws-code --opt type=none --opt device=/Users/mchin/workspaces/gplates-web-service --opt o=bind`

start and stop

`docker-compose up -d`

`docker-compose down -d`

## Helper scripts

- `start-postgis.sh` start PostGIS server
- `start-gws.sh` start GWS develop server
- `test-dev-server.sh` test if the develop server has been started successfully

Note: Add `postgis.gdal_enabled_drivers = 'ENABLE_ALL'` in postgres.conf to enable all GDAL driver(useful when export images from raster table)

Note: Use `http://localhost:18000/raster/query?lon=99.50&lat=-40.24&raster_name=age_grid_geek_2007` to test raster table
