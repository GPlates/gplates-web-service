#### Use docker container for development

* Run ``docker run -it --rm -v `pwd`:/gws -p 18000:80 gplates/gws /bin/bash``

* Inside the virtual machine: `cd /gws/gplates-web-service/django/GWS & python manage.py runserver 0.0.0.0:80`

* The dev server is at http://localhost:18000)


#### Update the docker image

Go to the root directory of this repository and run 

`docker build -f docker/Dockerfile -t gplates/gws .`

#### Run docker container in production env

`docker run -d -p 18000:80 --restart always gplates/gws`

The server is running at http://your-ip-address:18000. You may need to do some http requests redirection work.

You can try "--network host" argument. The following command will start a server listening on the 80 port of the host computer.

`docker run -d --network host --restart always gplates/gws`

