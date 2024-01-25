#
# to build this docker container image
# step 1: git clone https://github.com/GPlates/gplates-web-service.git
# step 2: go into folder gplates-web-service
# step 3: docker build -f docker/gws-amd64/Dockerfile -t gplates/gws:amd64 .
#

# if error, try with --no-cache option

FROM ubuntu:22.04

LABEL org.opencontainers.image.authors="michael.chin@sydney.edu.au"
LABEL version="0.1.0"

RUN apt-get update -y
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia 
RUN apt-get install -y python3 python3-pip 
RUN apt-get install -y apache2 apache2-dev libapache2-mod-wsgi-py3 
RUN apt-get install -y gmt gmt-dcw gmt-gshhg libpq-dev libgeos-dev libproj-dev proj-data proj-bin 
RUN pip3 install --upgrade pip
RUN pip3 install django djangorestframework uritemplate mod_wsgi numpy pandas scipy healpy requests netCDF4 pyshp psycopg2 
RUN pip3 install --use-deprecated=legacy-resolver cartopy
#RUN pip3 install --no-binary :all: psycopg2

RUN apt-get install -y ghostscript
RUN apt-get install -y ffmpeg

ADD ./docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

RUN rm /etc/apache2/sites-enabled/000-default.conf
RUN ln -s /gws/docker/gws.conf /etc/apache2/sites-enabled/gws.conf

RUN apt-get install -y wget

#install pygplates
RUN wget https://www.earthbyte.org/download/9079/ -O /pygplates_0.36.0_py310_ubuntu-22.04-amd64.deb
RUN apt-get install -y /pygplates_0.36.0_py310_ubuntu-22.04-amd64.deb
RUN rm /pygplates_0.36.0_py310_ubuntu-22.04-amd64.deb

RUN ln -s /gws/django/GWS/static/ /var/www/html/static

#RUN apt-get -y purge python-openssl
RUN apt-get -y  autoremove
RUN pip3 install --upgrade pyopenssl

RUN apt install -y gdal-bin libgdal-dev
RUN pip3 install GDAL geoserver-rest
RUN pip3 install python-dotenv
RUN pip3 install tzdata black
RUN pip3 install plate-model-manager --upgrade
RUN pip3 install redis

ADD . /gws
RUN mv /gws/django/GWS/env.template /gws/django/GWS/.env
RUN pmm download all /gws/django/GWS/data/model-repo/

# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-amd64 /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
CMD ["/startup.sh"]

ENV PYTHONPATH ${PYTHONPATH}:/usr/lib

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir /tmp/gws
RUN chown www-data /tmp/gws
RUN chown www-data /var/www

HEALTHCHECK CMD curl --fail -s "http://localhost:80/raster/query?lon=128.86&lat=-12.42&raster_name=crustal_thickness" || exit 1

EXPOSE 80

