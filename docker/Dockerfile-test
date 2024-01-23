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


ADD . /gws

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

EXPOSE 80

