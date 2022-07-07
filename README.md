# GPlates Web Service

The **GPlates Web Service** is a part of the on-going GPlates project funded by [AuScope](https://www.auscope.org.au/).
The web service is built upon [pygplates](https://www.gplates.org/docs/pygplates/index.html).
It allows users to utilize the pygplates functionalities without installing pygplates locally.
Users can send HTTP requests to https://gws.gplates.org to get the reconstruction results back.
This enables pygplates functionalities in any programming languanges and on any operation systems.

The web serivce is also containerized(https://hub.docker.com/r/gplates/gws). Users can choose to deploy the [Docker](https://www.docker.com/) containers locally
to enhance performance and data security.

The GPlates Web Service is created and maintained by [EarthByte](https://www.earthbyte.org) group at the [University of Sydney](https://www.sydney.edu.au/).

## Contents

- **django** -- folder contains source code files for backend services (using django framework).

- **docker** -- folder contains files for building Docker image

- **doc** -- documentation website. This doc website is built upon [gatsby-gitbook-starter](https://www.gatsbyjs.com/starters/hasura/gatsby-gitbook-starter/).

- **python** -- frontend python code

- examples of accessing the service from different languages (R,matlab,bash/GMT,python) have now been moved to https://github.com/siwill22/gws-examples

## 👍Docker

click 👉[here](docker/README.md) to see details about using Docker in development and production environment.

Note: Add `postgis.gdal_enabled_drivers = 'ENABLE_ALL'` in postgres.conf to enable all GDAL driver(useful when export images from raster table)

Note: Use `http://localhost:18000/raster/query?lon=99.50&lat=-40.24&raster_name=age_grid_geek_2007` to test raster table
