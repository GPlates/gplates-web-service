## Use docker container for development

* Go to the root directory of this repository and run  ``docker run -it --rm -v `pwd`:/gws -p 18000:80 gplates/gws /bin/bash``

* Inside the virtual machine: `cd /gws/django/GWS && python3 manage.py runserver 0.0.0.0:80`

* The dev server is at http://localhost:18000. **IMPORTANT: Make sure the BEDUG is set to True in settings.py**


## Update the docker image

Go to the root directory of this repository and run 

`docker build -f docker/Dockerfile -t gplates/gws .`


## Run docker container in production env

Go to the repository root directory, such as `/var/www/gplates-web-service`, and run

`docker run -d -v `pwd`:/gws -p 18000:80 --restart always gplates/gws`

The server is running at http://your-ip-address:18000. You may need to do some http requests redirection work.

You can try "--network host" argument. The following command will start a server listening on the 80 port of the host computer.
If you start the docker container with "--network host", the localhost and 127.0.0.1 inside docker container are pointing to the host computer. 

`docker run -d -v `pwd`:/gws --network host --restart always gplates/gws`
