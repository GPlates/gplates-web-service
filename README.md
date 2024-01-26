# GPlates Web Service

![Test](https://github.com/gplates/gplates-web-service/actions/workflows/test.yml/badge.svg)
![Build Docker](https://github.com/gplates/gplates-web-service/actions/workflows/build-and-push-docker.yml/badge.svg)
![Release Test](https://github.com/gplates/gplates-web-service/actions/workflows/release-test.yml/badge.svg)

The **🔥GPlates Web Service🔥** is a part of the on-going GPlates project funded by [AuScope](https://www.auscope.org.au/).
The web service is built upon [pygplates](https://www.gplates.org/docs/pygplates/index.html).
It allows users to utilize the pygplates functionalities without installing pygplates locally.
Users can send HTTP requests to https://gws.gplates.org to get the reconstruction results back.
This enables pygplates functionalities in any programming languanges and on any operation systems.

The web serivce is also containerized(https://hub.docker.com/r/gplates/gws). Users can choose to deploy the [Docker](https://www.docker.com/) containers locally
to enhance performance and data security.

The GPlates Web Service is created and maintained by [EarthByte](https://www.earthbyte.org) group at the [University of Sydney](https://www.sydney.edu.au/).

## 📂Contents

- **django** -- folder contains source code files for backend services (using django framework).

- **docker** -- folder contains files for building Docker image

- **doc** -- documentation website. This doc website is built upon [gatsby-gitbook-starter](https://www.gatsbyjs.com/starters/hasura/gatsby-gitbook-starter/).

- **examples** -- some examples to show how to use this web service

- **test** -- code for testing this web service

- examples of accessing the service from different languages (R,matlab,bash/GMT,python) have now been moved to https://github.com/siwill22/gws-examples

## 🐳Docker

click 👉[here](docker/README.md)👈 to see details about using Docker in development and production environment.

## 📚Documentation

[Go to GWS documentation website](https://gwsdoc.gplates.org/)

The Swagger UI is at https://gws.gplates.org/swagger-ui/

The OpenAPI schema is at https://gws.gplates.org/openapi

## 📮Contact

👉 [Contact EarthByte](https://www.earthbyte.org/contact-us-3/)

## 📝License

The GPlates Web Service is free software (also known as open-source software), licensed for distribution under the GNU [General Public License (GPL)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html), version 2.



