## 👉 Quick start 

To setup GPlates Web Service quickly, follow the steps in this "Quick start" section. The basic setup will start the Docker container using the built-in source code. 

- run the one-line command below to start a basic GPlates Web Service (You need [Docker](https://www.docker.com/get-started/) to run the commmand)

    ```
    docker run -d --rm -p 18000:80 gplates/gws
    ```

- verify the service is up and running.

    In your web browser, click [here](http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140)

    OR

    ```
    wget -qO - "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140" 
    ```
    
    OR

    ```
    curl "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140" 
    ```
     

👏👏👏Congratulations! At this point, the most basic GPlates Web Service is up and running. Now, if you're up for some challenges, read on.

## 👉 Use the latest source code from github repository

The source code included in the Docker image is the official release version. If you would like to use the latest source code from github repository, you need to follow the steps below.

- get the source code from github repository
```
git clone --depth 1 -b master https://github.com/GPlates/gplates-web-service gplates-web-service.git
```
- attach the volume when starting the service
```
docker run -d --rm -v /THE-ABSOLUTE-PATH-TO-YOUR-CURRENT-WORKING-DIRECTORY/gplates-web-service.git:/gws -p 18000:80 gplates/gws
```
- verify the service is up and running with wget, curl or web browser (see above)

## 👉 Start GWS with Docker compose

The official GWS setup includes the GPlates database and Redis cache. You can use the Docker compose to start the service along with the GPlates database and Redis cache.
    
- get the latest source code from github repository
```
git clone --depth 1 -b master https://github.com/GPlates/gplates-web-service gplates-web-service.git
```
- create a gplates network
```
docker network create --driver bridge gplates-net
```
- start the service
```
docker compose -f gplates-web-service.git/docker/docker-compose.yml up -d
```
- verify the service is up and running with wget, curl or web browser (see above)


## 👉 Use external Docker volumes

If you would like to use the latest source code from github repository and keep the database files on your host computer, follow the steps below. 

👀 👀 You need to change the paths accordingly in the steps below. 

- get the source code from github repository
```
git clone --depth 1 -b master https://github.com/GPlates/gplates-web-service gplates-web-service.git
```
- create a .env file from the template
```
cp gplates-web-service.git/django/GWS/env.template gplates-web-service.git/django/GWS/.env
```
- create GWS source code volume
```
docker volume create --name gws-code --opt type=none --opt device=/THE-ABSOLUTE-PATH-TO-YOUR-CURRENT-WORKING-DIRECTORY/gplates-web-service.git --opt o=bind
```
- create a folder for database files
```
mkdir gplates-db-data
```
- create database volume
```
docker volume create --name gplates-db-data --opt type=none --opt device=/THE-ABSOLUTE-PATH-TO-YOUR-CURRENT-WORKING-DIRECTORY/gplates-db-data --opt o=bind
```
- create a gplates network
```
docker network create --driver bridge gplates-net
```
- start the service
```
docker compose -f gplates-web-service.git/docker/docker-compose-external-volumes.yml up -d
```
- verify the service is up and running with wget, curl or web browser (see above)
- verify the database is working with this [link](http://localhost:18000/raster/query?lon=128.86&lat=-12.42&raster_name=crustal_thickness)
- (optional) use `psql gplates < gplates.sql` to restore GPlates database

## 👉 Docker images

The GWS Docker images are in two repositories, [Docker Hub](https://hub.docker.com/r/gplates/gws/tags) and [GitHub Packages](https://github.com/GPlates/gplates-web-service/pkgs/container/gws).

- `docker pull gplates/gws`
- `docker pull gplates/postgis`
- `docker pull ghcr.io/gplates/gws:latest`
- `docker pull ghcr.io/gplates/postgis:latest`




