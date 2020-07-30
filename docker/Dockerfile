#
# (in root folder ) docker build -f docker/Dockerfile -t gplates/gws .
#

FROM ubuntu:20.04

RUN apt-get update -y
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia 
RUN apt-get install -y python3 python3-pip apache2 apache2-dev libapache2-mod-wsgi 
RUN apt-get install -y gmt gmt-dcw gmt-gshhg libpq-dev
RUN pip3 install --upgrade pip
RUN pip3 install django mod_wsgi numpy pandas scipy healpy requests netCDF4 pyshp psycopg2
#RUN pip3 install --no-binary :all: psycopg2

RUN apt-get install -y python-mpltoolkits.basemap
RUN apt-get install -y ghostscript
RUN apt-get install -y ffmpeg

ADD . /usr/src/
RUN chmod o+w /usr/src/django/GWS/DATA/tmp
RUN chmod +x /usr/src/docker/startup.sh
RUN rm /etc/apache2/sites-enabled/000-default.conf
RUN cp /usr/src/docker/gws.conf /etc/apache2/sites-enabled/

#install pygplates
RUN apt-get install -y /usr/src/docker/pygplates-ubuntu-focal_2.2_1_amd64.deb
RUN rm /usr/src/docker/pygplates-ubuntu-focal_2.2_1_amd64.deb

RUN mkdir /tmp/gws
RUN chown www-data /tmp/gws

RUN mkdir /var/www/html/static
RUN cp /usr/src/django/GWS/static/* /var/www/html/static

RUN apt-get -y purge python-openssl
RUN apt-get -y  autoremove
RUN pip3 install --upgrade pyopenssl

# Add Tini
ENV TINI_VERSION v0.9.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
CMD ["/usr/src/docker/startup.sh"]

ENV PYTHONPATH ${PYTHONPATH}:/usr/lib:/usr/lib/pygplates/revision28

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 80

