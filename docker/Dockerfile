#
# to build this docker container image
# step 1: git clone https://github.com/GPlates/gplates-web-service.git
# step 2: go into folder gplates-web-service
# step 3: docker build -f docker/Dockerfile -t gplates/gws .
#

# if error, try with --no-cache option

FROM ubuntu:22.04

RUN apt-get update -y
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia 
RUN apt-get install -y python3 python3-pip 
RUN apt-get install -y apache2 apache2-dev libapache2-mod-wsgi-py3 
RUN apt-get install -y gmt gmt-dcw gmt-gshhg libpq-dev libgeos-dev libproj-dev proj-data proj-bin 
RUN pip3 install --upgrade pip
RUN pip3 install django mod_wsgi numpy pandas scipy healpy requests netCDF4 pyshp psycopg2 
RUN pip3 install --use-deprecated=legacy-resolver cartopy
#RUN pip3 install --no-binary :all: psycopg2

RUN apt-get install -y ghostscript
RUN apt-get install -y ffmpeg

RUN mkdir -p /usr/src/django/GWS/DATA/tmp
RUN chmod o+w /usr/src/django/GWS/DATA/tmp

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

ADD . /gws

# Add Tini
ENV TINI_VERSION v0.9.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
CMD ["/startup.sh"]

ENV PYTHONPATH ${PYTHONPATH}:/usr/lib:/usr/lib/pygplates/revision36

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir /tmp/gws
RUN chown www-data /tmp/gws
RUN chown www-data /var/www

EXPOSE 80

