# GPlates Web Service

![Test](https://github.com/gplates/gplates-web-service/actions/workflows/test.yml/badge.svg)
![Build Docker](https://github.com/gplates/gplates-web-service/actions/workflows/build-and-push-docker.yml/badge.svg)
![Release Test](https://github.com/gplates/gplates-web-service/actions/workflows/release-test.yml/badge.svg)

The **🔥GPlates Web Service🔥** is a part of the on-going GPlates project funded by [AuScope](https://www.auscope.org.au/). The web service is built upon [pygplates](https://www.gplates.org/docs/pygplates/index.html) and allows users to utilize the pygplates functionalities without installing pygplates locally. Users send HTTP requests to https://gws.gplates.org or the local [dockerized](https://hub.docker.com/r/gplates/gws) server, and the server will process the requests and send the reconstruction results back. The web service enables pygplates functionalities in any programming languange and on any operating system.

The GPlates Web Service is created and maintained by [EarthByte](https://www.earthbyte.org) group at the [University of Sydney](https://www.sydney.edu.au/).

## 🤔Why use GPlates Web Service

- cross-platform and language-independent -- the service can be used in any programming languange and on any operating system
- scalability -- offload workload to servers, cluster, grid or Cloud to improve performance and support more concurrent users
- automated plate model management -- provide plenty plate models out of the box
- easy software deployment and upgrade -- avoid the hassle of software installation

## 🚀Quick start

👉 Use the GPlates Web Service in a web browser

- Step 1: open this link in a web browser <https://gws.gplates.org/reconstruct/reconstruct_points/?lons=95,142&lats=54,-33&time=140&model=MULLER2019>
- Step 2: done and check the paleo-coordinates in the web browser

```
{"type": "MultiPoint", "coordinates": [[84.9862, 59.2575], [123.374, -65.7611]]}
```

The GPlates Web Service server returns a valid GeoJSON MultiPoint geometry that contains the paleo-coordinates of two present-day locations at 140Ma. The paleo-coordinates were calculated according to the plate reconstruction model [Muller2019](https://www.earthbyte.org/muller-et-al-2019-deforming-plate-reconstruction-and-seafloor-age-grids-tectonics/). 

👉 Use GPlates Web Service Python Client/Proxy

See the examples at <https://github.com/michaelchin/gplates-python-proxy/blob/main/README.md>

👉 Setup your own server

Our https://gws.gplates.org is for **demostration purpose only** because we cannot afford an industrial level computer server/cluster. **📌Hence, for better performance and security, you are encouraged to setup your own servers if you need to process a substantial volume of data.**

- Step 1: `git clone https://github.com/GPlates/gplates-web-service gplates-web-service.git`
- Step 2: `docker compose -f gplates-web-service.git/docker/docker-compose.yml up -d`
- Step 3: open this link in a web browser <http://localhost:18000/reconstruct/reconstruct_points/?lons=95,142&lats=54,-33&time=140&model=MULLER2019>

See [docker/README.md](docker/README.md) for the details.

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

The GPlates Web Service is free software (also known as open-source software), licensed for distribution under the GNU [General Public License (GPL)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html), version 2. Contact [Earthbyte](https://www.earthbyte.org/contact-us-3/) group about the details of the software licensing.



