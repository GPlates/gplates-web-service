#
# to build this docker container image
# step 1: git clone https://github.com/GPlates/gplates-web-service.git
# step 2: go into folder gplates-web-service
# step 3: docker build -f docker/Dockerfile -t gplates/gws .
#

# if error, try with --no-cache option

FROM ubuntu:22.04

LABEL org.opencontainers.image.authors="michael.chin@sydney.edu.au"
LABEL version="v0.2.1"

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia 

RUN apt-get update -y
RUN apt-get install -y wget python3 python3-pip less gdal-bin libgdal-dev
RUN apt-get install -y apache2 apache2-dev libapache2-mod-wsgi-py3 ghostscript ffmpeg
RUN apt-get install -y gmt gmt-dcw gmt-gshhg libpq-dev libgeos-dev libproj-dev proj-data proj-bin 

RUN pip3 install --upgrade pip
RUN pip3 install django djangorestframework uritemplate mod_wsgi numpy==1.26.4 pandas scipy healpy requests netCDF4 pyshp psycopg2 
RUN pip3 install Cartopy pyopenssl==22.1.0 GDAL geoserver-rest python-dotenv tzdata redis
RUN pip3 install plate-model-manager --upgrade

ADD ./docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

RUN rm /etc/apache2/sites-enabled/000-default.conf
RUN ln -s /gws/docker/gws.conf /etc/apache2/sites-enabled/gws.conf

#install pygplates
ADD ./docker/download-pygplates.sh /
RUN chmod +x /download-pygplates.sh
RUN /download-pygplates.sh
RUN apt-get install -y /pygplates_0.36.0_py310_ubuntu-22.04.deb
RUN rm /pygplates_0.36.0_py310_ubuntu-22.04.deb && rm /download-pygplates.sh

RUN ln -s /gws/django/GWS/static/ /var/www/html/static

ADD . /gws
RUN mv /gws/django/GWS/env.template /gws/django/GWS/.env
RUN pmm download all /gws/django/GWS/data/model-repo/

# Add Tini
RUN apt-get install -y tini
ENTRYPOINT ["/tini", "--"]
CMD ["/startup.sh"]

ENV PYTHONPATH=/usr/lib
ENV PAGER=less

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir /tmp/gws
RUN chown www-data /tmp/gws
RUN chown www-data /var/www

HEALTHCHECK CMD curl --fail -s "http://localhost:80/raster/query?lon=128.86&lat=-12.42&raster_name=crustal_thickness" || exit 1

EXPOSE 80

