#
# Check the password in create-gws-db.sql before building this docker image
#
# step 1: git clone https://github.com/GPlates/gplates-web-service.git
# step 2: go into folder gplates-web-service
# step 3: `docker build -f docker/postgis/Dockerfile -t gplates/postgis .`
#
# if error, try with --no-cache option
#

FROM ubuntu:24.04

LABEL org.opencontainers.image.authors="michael.chin@sydney.edu.au"
LABEL version="v1.1.0"

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia/Sydney

RUN apt-get update
RUN apt-get install -y wget less

#install postgis
# apt-key is removed as of Debian 13/Ubuntu 24.04+, so the PGDG signing key
# is dearmored into its own keyring file and referenced via signed-by=
# instead of the old apt-key add approach.
RUN apt -y install gnupg2 lsb-release
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list
RUN apt update
RUN apt install -y  postgis postgresql-18-postgis-3

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
ADD docker/postgresql.conf /etc/postgresql/18/main/
ADD docker/pg_hba.conf /etc/postgresql/18/main/
RUN chown postgres:postgres /etc/postgresql/18/main/*

# Add Tini
RUN apt-get install -y tini
ENTRYPOINT ["/usr/bin/tini", "--"]

ENV PAGER=less

CMD ["sh", "-c", "/etc/init.d/postgresql start 18; tail -f /dev/null"]

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

HEALTHCHECK CMD pg_isready -U gplates -d gplates

EXPOSE 5432

