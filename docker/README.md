## 👉 Quick start 

To set up GPlates Web Service quickly, follow the steps in this "Quick start" section. The service will use the source code in the Docker image. 

- run the one-line command below to start a basic GPlates Web Service You need [Docker](https://www.docker.com/get-started/) to run the command.

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

## 👉 Use the latest source code from GitHub repository

The source code included in the Docker image is the official release version. If you would like to use the latest source code from GitHub repository, you need to follow the steps below.

- get the source code from GitHub repository
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
    
- get the latest source code from GitHub repository
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

If you would like to use the latest source code from GitHub repository and keep the database files on your host computer, follow the steps below. 

👀 👀 You need to change the paths accordingly in the steps below. 

- get the source code from GitHub repository
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
- create database volume

  **Recommended**: a plain Docker-managed volume. Docker owns the storage directly, which avoids host/container file-ownership mismatches (see `notes.md` for a real example of this biting on macOS but not Linux).
  ```
  docker volume create --name gplates-db-data
  ```

  Alternative: bind-mount a specific folder on your host instead, if you need to inspect or back up the database files directly from the host filesystem. This is more prone to the UID/permission mismatch mentioned above, and you lose the safety of Docker managing the storage lifecycle for you.
  ```
  mkdir gplates-db-data
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

## 👉 Serve GWS under your own host name

Django checks the `Host` header of every request against `ALLOWED_HOSTS` in `django/GWS/GWS/settings.py`. The default list covers the gplates.org servers, the `gws` container host name and `localhost`/`127.0.0.1`, so the quick start and the Docker compose setups work out of the box.

If you serve GWS under a host name of your own, add it to the `GWS_ALLOWED_HOSTS` environment variable (a comma-separated list), otherwise Django answers those requests with `400 Bad Request`.

```
docker run -d --rm -e GWS_ALLOWED_HOSTS=gws.my-institution.edu,localhost -p 18000:80 gplates/gws
```

The variable can also go in `django/GWS/.env` (see `django/GWS/env.template`).

## 👉 Docker images

The GWS Docker images are in two repositories, [Docker Hub](https://hub.docker.com/r/gplates/gws/tags) and [GitHub Packages](https://github.com/GPlates/gplates-web-service/pkgs/container/gws).

- `docker pull gplates/gws`
- `docker pull gplates/postgis`
- `docker pull ghcr.io/gplates/gws:latest`
- `docker pull ghcr.io/gplates/postgis:latest`




