# GPlates Web Service

The **GPlates Web Service** is a part of the on-going GPlates project funded by [AuScope](https://www.auscope.org.au/). 
The web service is built upon [pygplates](https://www.gplates.org/docs/pygplates/index.html). 
It allows users to utilize the pygplates functionalities without installing pygplates locally. 
Users can send HTTP requests to https://gws.gplates.org to get the reconstruction results back. 
This enables pygplates functionalities in any programming languanges and on any operation systems.

The web serivce is also containerized(https://hub.docker.com/r/gplates/gws). Users can choose to deploy the [Docker](https://www.docker.com/) containers locally 
to enhance performance and data security. 

The GPlates Web Service is created and maintained by [EarthByte](https://www.earthbyte.org) group at the [University of Sydney](https://www.sydney.edu.au/).


## Contents

- **django** -- folder contains source code files for backend services (using django framework).  

- **docker** -- folder contains files for building Docker image

- **doc** -- documentation website. This doc website is built upon [gatsby-gitbook-starter](https://www.gatsbyjs.com/starters/hasura/gatsby-gitbook-starter/).

- **python** -- frontend python code

- examples of accessing the service from different languages (R,matlab,bash/GMT,python) have now been moved to https://github.com/siwill22/gws-examples


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



