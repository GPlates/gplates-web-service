##
#

FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y python python-pip apache2 apache2-dev libapache2-mod-wsgi 
RUN pip install --upgrade pip
RUN pip install django mod_wsgi numpy pandas scipy healpy

ADD . /usr/src/
RUN chmod +x /usr/src/docker/startup.sh
RUN rm /etc/apache2/sites-enabled/000-default.conf
RUN cp /usr/src/docker/gws.conf /etc/apache2/sites-enabled/

# install dependencies for pygplates
RUN apt-get install -y libglew-dev
RUN apt-get install -y python2.7-dev
RUN apt-get install -y libboost-dev libboost-python-dev libboost-thread-dev libboost-program-options-dev libboost-test-dev libboost-system-dev
RUN apt-get install -y libqt4-dev
RUN apt-get install -y libgdal1-dev
RUN apt-get install -y libcgal-dev
RUN apt-get install -y libproj-dev
RUN apt-get install -y libqwt-dev
RUN apt-get install -y libxrender-dev libice-dev libsm-dev libfreetype6-dev libfontconfig1-dev

RUN dpkg -i /usr/src/docker/pygplates_2.0_amd64.deb

# Add Tini
ENV TINI_VERSION v0.9.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
CMD ["/usr/src/docker/startup.sh"]


EXPOSE 80

