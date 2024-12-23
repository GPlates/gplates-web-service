

## ☣👀Warning: The notes in this page are meant for development team only. Others may fail to understand them.☣👀 

### Use the "build-docker-images" branch to build Docker images.

- merge master branch to the "build-docker-images" branch
- update build-docker-images.txt in the "build-docker-images" branch
- push (you don't need to remove the old docker images. the images will be updated.)
- the new docker images will be built by the github action

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

☣ You need to change the folder paths in the steps below according to your computer setup. 

- `git clone https://github.com/GPlates/gplates-web-service gplates-web-service.git`
- `cp gplates-web-service.git/django/GWS/env.template gplates-web-service.git/django/GWS/.env`
- `docker volume create --name gws-code --opt type=none --opt device=/THE-ABSOLUTE-PATH-TO-YOUR-SOURCE-CODE-FOLDER/gplates-web-service.git --opt o=bind`
- `docker volume create --name gws-db-data --opt type=none --opt device=/THE-ABSOLUTE-PATH-TO-YOUR-SOURCE-CODE-FOLDER/gws-db-data --opt o=bind`
- `docker compose -f gplates-web-service.git/docker/docker-compose-code-and-db-volume.yml up -d`

👀 👀 You may not have to do the steps below. But sometimes you do. I did not have to do this on my Ubuntu server. But I had to do it on my Macbook. Attention, you need to change the docker container name accordingly.

- `docker exec -ti docker-gws-postgis-1 /bin/bash`
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

run scripts/start-gws-dev.sh

**👀 IMPORTANT: Make sure the BEDUG is set to True in .env 👀**

## 👉 Build the docker images

see **.github/workflows/build-and-push-docker.yml** and **.github/workflows/release-test.yml**

## 👉 Run docker container in production env

- see the section above "**Keep the database data on host computer**"
- edit file ".env" accordingly
- The server is running at http://your-ip-address:18000. You may need to do some http requests redirection work.

You can try "--network host" argument. The command below will start a server listening on the 80 port of the host computer.

If you start the docker container with "--network host", the localhost and 127.0.0.1 inside docker container are pointing to the host computer.

`` docker run -d -v `pwd`:/gws --network host --restart always gplates/gws ``

## 👉 Docker compose

run postgis: `docker-compose run --rm -d --service-ports gws-postgis`

run gws for debug `docker-compose run --rm --service-ports gws /bin/bash`

create volume from local folder:

`docker volume create --name gws-code --opt type=none --opt device=/Users/mchin/workspace/gplates-web-service --opt o=bind`

☣ when copying DB data from other computer, log into PostGIS docker container and change the owner and permission accordingly. Otherwise the Postgres would not start.

start and stop

`docker-compose up -d`

`docker-compose down`

## 👉 Helper scripts

- `start-postgis.sh` start PostGIS server
- `start-gws.sh` start GWS develop server
- `test-dev-server.sh` test if the develop server has been started successfully

## 👉 Notes

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