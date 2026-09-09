#
# to build this docker container image
# step 1: git clone https://github.com/GPlates/gplates-web-service.git
# step 2: go into folder gplates-web-service
# step 3: docker build -f docker/Dockerfile -t gplates/gws .
#
# if error, try with --no-cache option
#

FROM mambaorg/micromamba:2.9.0

LABEL org.opencontainers.image.authors="michael.chin@sydney.edu.au"
LABEL version="v1.1.0"

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia/Sydney

USER root

# System packages only -- no python3/python3-pip and no
# libapache2-mod-wsgi-py3 here. Every Python package (Django, numpy,
# GDAL, Cartopy, GMT, and mod_wsgi's own Apache module -- see below) comes
# from the micromamba environment instead, so there is exactly one Python
# and one set of package versions in this image, not two.
#
# apache2-dev is needed so `pip install mod_wsgi` (below) can compile the
# Apache module against this exact Apache build.
RUN apt-get update && apt-get install -y --no-install-recommends \
      apache2 \
      apache2-dev \
      ffmpeg \
      libsm6 \
      libxext6 \
      ghostscript \
      wget \
      curl \
      less \
      tini && \
    rm -rf /var/lib/apt/lists/*

USER $MAMBA_USER
COPY --chown=$MAMBA_USER:$MAMBA_USER ./docker/env.yaml /tmp/env.yaml
RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes

USER root

# Apache/mod_wsgi is started as a system service (service apache2 start),
# not through micromamba's own activation wrapper, so it never gets
# LD_LIBRARY_PATH pointed at this environment's lib/ directory. Native
# libraries that conda-forge packages need at runtime (e.g. netCDF4's
# libnetcdf.so, GDAL's, GEOS's, PROJ's) would otherwise fail to load with
# "cannot open shared object file" the moment Apache imports them. Register
# the environment's lib directory with the system's dynamic linker instead,
# so it's found unconditionally by every process, not just ones that went
# through `micromamba activate`/`micromamba run`.
RUN echo "${MAMBA_ROOT_PREFIX}/lib" > /etc/ld.so.conf.d/conda.conf && ldconfig

USER $MAMBA_USER
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Compile mod_wsgi from source (via pip, inside the activated environment)
# against *this* Python and *this* Apache. A prebuilt conda-forge mod_wsgi
# binary can't guarantee ABI compatibility with whatever Apache build ends
# up in this image, so it's built locally instead, where both are known.
RUN pip install --no-cache-dir mod_wsgi && \
    pip install --no-cache-dir --upgrade plate-model-manager

USER root

# Ask mod_wsgi itself where it (and this environment's Python) actually are,
# instead of hand-writing LoadModule/WSGIPythonHome paths that change across
# mod_wsgi/micromamba/Python versions.
RUN mod_wsgi-express module-config > /etc/apache2/conf-enabled/mod_wsgi.conf

RUN rm -f /etc/apache2/sites-enabled/000-default.conf && \
    ln -s /gws/docker/gws.conf /etc/apache2/sites-enabled/gws.conf

RUN ln -s /gws/django/GWS/static/ /var/www/html/static

ADD ./docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

ADD . /gws
RUN mv /gws/django/GWS/env.template /gws/django/GWS/.env
RUN pmm download all /gws/django/GWS/data/model-repo/
#RUN chown www-data:www-data /pmm.log

RUN mkdir -p /tmp/gws && chown www-data /tmp/gws && chown www-data /var/www

# Make the environment's binaries (pmm, python, etc.) resolvable at
# container runtime too, not just during the build -- ENTRYPOINT below
# replaces micromamba's own activation wrapper, and startup.sh's runtime
# fallback call to `pmm` needs this.
ENV PATH="${MAMBA_ROOT_PREFIX}/bin:${PATH}"
ENV PAGER=less

# Add Tini
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/startup.sh"]

HEALTHCHECK CMD curl --fail -s "http://localhost:80/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140" || exit 1
#HEALTHCHECK CMD curl --fail -s "http://localhost:80/raster/query?lon=128.86&lat=-12.42&raster_name=crustal_thickness" || exit 1

EXPOSE 80
