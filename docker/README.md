## 👉 Quick start 

If you would like to try the GPlates Web Service very quickly, follow the steps in this "quick start" section. The steps will start the Docker container using the built-in source code. 

- start the GPlates Web Service

    `docker run -d --rm -p 18000:80 gplates/gws`

- verify the service is up and running.

    In your web browser, click [here](http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140)

    OR

    - `wget -qO - "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140" `
    - `curl "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140" `
     

👏👏👏Congratulations! At this point, the most basic GPlates Web Service is up and running.

## 👉 Use the source code on the host computer to start the GPlates Web Service 

- `git clone --depth 1 -b master https://github.com/GPlates/gplates-web-service gplates-web-service.git`
- `docker run -d --rm -v /THE-ABSOLUTE-PATH-TO-YOUR-CURRENT-WORKING-DIRECTORY/gplates-web-service.git:/gws -p 18000:80 gplates/gws`
- verify the service is up and running with wget, curl or web browser (see above)

## 👉 Start the GPlates Web Service with Docker compose

Alternatively, you can also use Docker compose to start the GPlates Web Service along with GPlates database and Redis cache.
    
- `git clone --depth 1 -b master https://github.com/GPlates/gplates-web-service gplates-web-service.git`
- `docker network create --driver bridge gplates-net`
- `docker compose -f gplates-web-service.git/docker/docker-compose.yml up -d`
- verify the service is up and running with wget, curl or web browser (see above)


## 👉 Use external Docker volumes

If you would like to use the latest source code from github.com to run the service or keep the database data on the host computer, follow the steps below. 

👀 👀 You need to change the folder paths in the steps below according to your computer setup. 

- `git clone --depth 1 -b master https://github.com/GPlates/gplates-web-service gplates-web-service.git`
- `cp gplates-web-service.git/django/GWS/env.template gplates-web-service.git/django/GWS/.env`
- `docker volume create --name gws-code --opt type=none --opt device=/THE-ABSOLUTE-PATH-TO-YOUR-CURRENT-WORKING-DIRECTORY/gplates-web-service.git --opt o=bind`
- `mkdir gplates-db-data`
- `docker volume create --name gplates-db-data --opt type=none --opt device=/THE-ABSOLUTE-PATH-TO-YOUR-CURRENT-WORKING-DIRECTORY/gplates-db-data --opt o=bind`
- `docker compose -f gplates-web-service.git/docker/docker-compose-external-volumes.yml up -d`
- verify the service is up and running with wget, curl or web browser (see above)
- verify the database with "http://localhost:80/raster/query?lon=128.86&lat=-12.42&raster_name=crustal_thickness"
- (optional) use `psql gplates < gplates.sql` to restore gplates database

## 👉 Docker images

The Docker images are in two repositories, Docker Hub and GitHub Packages.

- `docker pull gplates/gws`
- `docker pull gplates/postgis`
- `docker pull ghcr.io/gplates/gws:latest`
- `docker pull ghcr.io/gplates/postgis:latest`

We also use Redis Docker image.

- `docker pull redis`





