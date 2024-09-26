#
# Check the password in create-gws-db.sql before building this docker image
#
# step 1: git clone https://github.com/GPlates/gplates-web-service.git
# step 2: go into folder gplates-web-service
# step 3: docker build -f docker/postgis/Dockerfile -t gplates/postgis .
#
# if error, try with --no-cache option
#

FROM ubuntu:22.04

LABEL org.opencontainers.image.authors="michael.chin@sydney.edu.au"
LABEL version="v0.2.1"

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia

RUN apt-get update
RUN apt-get install -y wget less

#install postgis
RUN apt -y install gnupg2
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get install -y lsb-release
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | tee  /etc/apt/sources.list.d/pgdg.list
RUN apt update
RUN apt install -y  postgis postgresql-15-postgis-3

#initialize DB
ADD docker/init-db.sh /workspace/
ADD docker/create-gplates-db.sql /workspace/
ADD docker/gplates-db-restore.sql /workspace/
ADD test/crustal_thickness.sql.gz /workspace
RUN gunzip /workspace/crustal_thickness.sql.gz
RUN chmod +x /workspace/init-db.sh
USER postgres
RUN cd /workspace/ && ./init-db.sh
USER root

#update postgres configuration file 
ADD docker/postgresql.conf /etc/postgresql/15/main/
ADD docker/pg_hba.conf /etc/postgresql/15/main/
RUN chown postgres:postgres /etc/postgresql/15/main/*

# Add Tini
RUN apt-get install -y tini
ENTRYPOINT ["/tini", "--"]

ENV PAGER=less

CMD ["sh", "-c", "/etc/init.d/postgresql start 15; tail -f /dev/null"]

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

HEALTHCHECK CMD pg_isready -U gplates -d gplates

EXPOSE 5432

