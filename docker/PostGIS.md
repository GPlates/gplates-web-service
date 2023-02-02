### Quick Start

- Step 1: Build the docker image

  Check the password in create-gws-db.sql before building this docker image

  `docker build -f docker/Dockerfile-postgis -t gplates/postgis .`

- Step 2: Run PostGIS in testing env

  Start the database(on host computer):

  `docker run --rm -it --name gws-postgis -e POSTGRES_PASSWORD=mysecretpassword -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main -p 5432:5432 --network gws-net gplates/postgis`

  Test the database(on host computer):

  `psql -d gplates -h localhost -U gplates`

- Step 3: If the database data folder is empty, you need to log into the docker container and call **initdb** on the folder first.

  `/usr/lib/postgresql/12/bin/initdb -D /var/lib/postgresql/data`

- Step 4: After "initdb", You also need to log into the container, `su postgres` and run `cd /workspace/ && ./init-db.sh`

- Step 5: import rasters with `psql -d gplates -f age_grid.sql` or `psql gplates < data_base_dump`

### Some tips

- Run PostGIS in production env

  `docker run --restart always --name gws-postgis -e POSTGRES_PASSWORD=mysecretpassword -d -v /Users/mchin/workspaces/gws-db-data:/var/lib/postgresql/12/main gplates/postgis`

- Log into the running container

  `docker exec -ti gws-postgis /bin/bash`

- Create the sql file from a raster

  `raster2pgsql -s 4326 -I -C -M Seton_etal_2020_PresentDay_AgeGrid.nc -F -t 100x100 public.age_grid > age_grid.sql`

- Import the sql file into DB

  `psql -d gplates -f age_grid.sql`

- create volume from local folder:

  `docker volume create --name gws-code --opt type=none --opt device=/Users/mchin/workspaces/gplates-web-service --opt o=bind`

  `docker volume ls`

  `docker volume inspect gws-code`
