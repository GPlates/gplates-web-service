#
# (in root folder ) docker build -f docker/Dockerfile -t gplates/gws .
#

FROM ubuntu:20.04

RUN apt-get update -y
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia 
RUN apt-get install -y python3 python3-pip apache2 apache2-dev libapache2-mod-wsgi-py3 
RUN apt-get install -y gmt gmt-dcw gmt-gshhg libpq-dev
RUN pip3 install --upgrade pip
RUN pip3 install django mod_wsgi numpy pandas scipy healpy requests netCDF4 pyshp psycopg2
#RUN pip3 install --no-binary :all: psycopg2

RUN apt-get install -y python3-mpltoolkits.basemap
RUN apt-get install -y ghostscript
RUN apt-get install -y ffmpeg

RUN mkdir -p /usr/src/django/GWS/DATA/tmp
RUN chmod o+w /usr/src/django/GWS/DATA/tmp

ADD ./docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

RUN rm /etc/apache2/sites-enabled/000-default.conf
RUN ln -s /gws/docker/gws.conf /etc/apache2/sites-enabled/gws.conf

#install pygplates
ADD ./docker/pygplates-ubuntu-focal_2.2_1_amd64.deb /pygplates-ubuntu-focal_2.2_1_amd64.deb
RUN apt-get install -y /pygplates-ubuntu-focal_2.2_1_amd64.deb
RUN rm /pygplates-ubuntu-focal_2.2_1_amd64.deb

RUN ln -s /gws/django/GWS/static/ /var/www/html/static

RUN apt-get -y purge python-openssl
RUN apt-get -y  autoremove
RUN pip3 install --upgrade pyopenssl

#basemap does not work with the new matplotlib.
#basemap should be replaced with cartopy
RUN pip3 uninstall -y matplotlib 

# Add Tini
ENV TINI_VERSION v0.9.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
CMD ["/startup.sh"]

ENV PYTHONPATH ${PYTHONPATH}:/usr/lib:/usr/lib/pygplates/revision28

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir /tmp/gws
RUN chown www-data /tmp/gws

EXPOSE 80

