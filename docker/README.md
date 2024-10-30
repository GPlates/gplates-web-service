## 👉 Quick start 

If you would like to try the GPlates Web Service very quickly, follow the steps in this "quick start" section. The steps will start the docker container using the built-in source code. 

- start the GPlates Web Service

    `docker run -d --rm -p 18000:80 gplates/gws`

- verify the service is up and running.

    In your web browser, click [here](http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140)

    OR

    - `wget -O test.json "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140" `
    - `curl "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140" `
     

👏👏👏Congratulations! At this point, the GPlates Web Service is up and running.

## 👉 Use the latest code from github.com to run the service 

👀 👀 You need to change the folder paths in the steps below according to your computer setup. 

- `git clone https://github.com/GPlates/gplates-web-service gplates-web-service.git`
- `cp gplates-web-service.git/django/GWS/env.template gplates-web-service.git/django/GWS/.env`
- `docker volume create --name gws-code --opt type=none --opt device=/THE-ABSOLUTE-PATH-TO-YOUR-SOURCE-CODE-FOLDER/gplates-web-service.git --opt o=bind`
- `docker compose -f gplates-web-service.git/docker/docker-compose-code-volume.yml up -d`
- verify the service is up and running with wget, curl or web browser (see above)

## 👉 Docker images

The docker images are in two repositories, Docker Hub and GitHub Packages.

- `docker pull gplates/gws`
- `docker pull gplates/postgis`
- `docker pull ghcr.io/gplates/gws:latest`
- `docker pull ghcr.io/gplates/postgis:latest`

You also need Redis image.

- `docker pull redis`

Use the "build-docker-images" branch to build Docker images.

- merge master branch to the "build-docker-images" branch
- update build-docker-images.txt in the "build-docker-images" branch
- push



