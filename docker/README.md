## 👉 Quick start 

If you would like to try the GPlates Web Service very quickly, follow the steps in this "quick start" section. The steps will start the docker container using the built-in source code. 

- run the with docker-compose

    - `git clone https://github.com/GPlates/gplates-web-service gplates-web-service.git`
    - `cd gplates-web-service.git`
    - `cd docker`
    - `docker-compose up -d`

- verify the service is up and running.

    - `wget -O test.json "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012" `
    - or `curl "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012" `
    - or use web browser if you have GUI

## 👉 Use the latest code from github.com to run the service 

- `git clone https://github.com/GPlates/gplates-web-service gplates-web-service.git`
- `cd gplates-web-service.git/docker`
- `docker-compose run --rm --service-ports gws-postgis`
- `docker-compose run --rm --service-ports redis`
- ``docker run -it --rm -v `pwd`:/gws -p 18000:80 gplates/gws``
- verify the service is up and running with wget, curl or web browser

Alternatively, 

you can write a customized docker-compose.yml, like Michael Chin did. See [docker-compose-mc.yml](docker-compose-mc.yml)

## 👀 Warning: The notes from this line below are meant for Michael Chin. Other people might fail to understand them. Ask him! 👀 

## 👉 Setup PostGIS database

- pull the postgis docker image from docker hub

    `docker pull gplates/postgis`

- run the postgis docker image

    `docker run -it --name gws-postgis -p 5432:5432 gplates/postgis`

- go inside the postgis docker container and change password for user gplates

    - `docker exec -ti gws-postgis /bin/bash`
    - `su postgres`
    - `ALTER USER gplates WITH PASSWORD 'new_password';`

- get gplates.sql and restore the database

    - `docker cp gplates.sql gws-postgis:/tmp/`(on host computer)
    - `docker exec -ti gws-postgis /bin/bash`
    - `su postgres`
    - `psql gplates < /tmp/gplates.sql`

- update your .env file accordingly and verify the DB

    `curl "http://localhost:18000/raster/query?lon=99.50&lat=-40.24&raster_name=age_grid_geek_2007"`


## 👉 Keep the database data on host computer

- `docker run -it --rm --name gws-postgis -v /Users/mchin/workspace/gws-db-data:/var/lib/postgresql/15/main -p 5432:5432 gplates/postgis`
- `docker exec -ti gws-postgis /bin/bash`
- `chown postgres:postgres -R /var/lib/postgresql/15/main/`
- `su postgres`
- `/usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/15/main`
- `cd /workspace/ && ./init-db.sh`
- continue to restore the database from gplates.sql


## 👉 Backup database

- `docker exec -ti gws-postgis /bin/bash`
- `su postgres`
- `cd tmp`
- `pg_dump gplates > gplates.sql` (pg_dump --no-owner -d gplates -t raster.age_grid_geek_2007 > age_grid_geek_2007.sql)
- `docker cp gws-postgis:/tmp/gplates.sql ~`(on host computer)


## 👉 Use docker container for development

- Create **gws-net** if haven't `docker network create --driver bridge gws-net`
- Go to the root directory of this repository and run `` docker run -it --rm -v `pwd`:/gws -p 18000:80 --network gws-net gplates/gws /bin/bash ``
- Go to folder "django/GWS/", run `copy env.template .env` and edit file ".env" according to the database configuration. The host name is postgis container name, such as gws-postgis
- Start the database `docker run --rm -it --name gws-postgis -v /Users/mchin/workspace/gws-db-data:/var/lib/postgresql/15/main --network gws-net gplates/postgis`
- Inside the virtual machine: `cd /gws/django/GWS && python3 manage.py runserver 0.0.0.0:80`
- `curl "http://localhost:18000/raster/query?lon=99.50&lat=-40.24&raster_name=age_grid_geek_2007"`
- `curl "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012"`

**👀 IMPORTANT: Make sure the BEDUG is set to True in .env 👀**


## 👉 Build the docker images

### Build GWS docker image

- go to the root directory of this repository 
- `cp django/GWS/env.template django/GWS/.env`
- `docker build -f docker/Dockerfile -t gplates/gws . --no-cache`

### Build postgis docker image

- go to the root directory of this repository 
- change the password in docker/create-gws-db.sql
- `docker build -f docker/Dockerfile-postgis -t gplates/postgis . --no-cache`

## 👉 Run docker container in production env

- Go to folder "%{git-repo-root}/django/GWS/", run `copy env.template .env` and edit file ".env" according to the database configuration
- Start the database 
    
    `docker run -d --name gws-postgis -v /Users/mchin/workspace/gws-db-data:/var/lib/postgresql/15/main --network gws-net --restart always gplates/postgis`

- Go to the repository root directory, such as `/var/www/gplates-web-service`, and run

    `` docker run -d -v `pwd`:/gws -p 18000:80 --network gws-net --restart always gplates/gws ``

The server is running at http://your-ip-address:18000. You may need to do some http requests redirection work.

You can try "--network host" argument. The command below will start a server listening on the 80 port of the host computer.

If you start the docker container with "--network host", the localhost and 127.0.0.1 inside docker container are pointing to the host computer.

`` docker run -d -v `pwd`:/gws --network host --restart always gplates/gws ``


## 👉 Docker compose

run postgis: `docker-compose run --rm --service-ports gws-postgis`

run gws for debug `docker-compose run --rm --service-ports gws /bin/bash`

create volume from local folder:

`docker volume create --name gws-code --opt type=none --opt device=/Users/mchin/workspace/gplates-web-service --opt o=bind`

⚠ when copying DB data from other computer, log into PostGIS docker container and change the owner and permission accordingly. Otherwise the Postgres would not start.

start and stop

`docker-compose up -d`

`docker-compose down`

## 👉 Helper scripts

- `start-postgis.sh` start PostGIS server
- `start-gws.sh` start GWS develop server
- `test-dev-server.sh` test if the develop server has been started successfully

## 👉 Notes

### Run PostGIS in testing env

Start the database(on host computer): `docker run --rm -it --name gws-postgis -v /Users/mchin/workspace/gws-db-data:/var/lib/postgresql/15/main -p 5432:5432 --network gws-net gplates/postgis`

Test the database(on host computer): `psql -d gplates -h localhost -U gplates`

### Run PostGIS in production env

`docker run --restart always --name gws-postgis -d -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main gplates/postgis`

### Log into the running container

`docker exec -ti gws-postgis /bin/bash`

### Create the sql file from a raster

`raster2pgsql -s 4326 -I -C -M Seton_etal_2020_PresentDay_AgeGrid.nc -F -t 100x100 public.age_grid > age_grid.sql`

### Import the sql file into DB

`psql -d gplates -f age_grid.sql`

### Use user-defined docker network

- `docker network create --driver bridge gws-net` (bridge is the default docker network)
- Use `--network gws-net` parameter to start docker containers
- In GWS server container, use `psql -d gplates -h gws-postgis -U gplates` to test DB

### Create and push manifest

- `docker manifest create gplates/postgis gplates/postgis:amd64 gplates/postgis:arm64`
- `docker manifest push gplates/postgis`

Note: Add `postgis.gdal_enabled_drivers = 'ENABLE_ALL'` in postgres.conf to enable all GDAL driver(useful when export images from raster table)

Note: Use `http://localhost:18000/raster/query?lon=99.50&lat=-40.24&raster_name=age_grid_geek_2007` to test raster table
