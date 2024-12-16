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
- easy software deployment and upgrade -- avoid the hassle of software installation and upgrade

## 🚀Quick start

👉 Use the GPlates Web Service in a web browser

- Step 1: open this link in a web browser <https://gws.gplates.org/reconstruct/reconstruct_points/?lons=95,142&lats=54,-33&time=140&model=MULLER2019>
- Step 2: check the paleo-coordinates in the web browser

```
{"type": "MultiPoint", "coordinates": [[62.6938, 58.8486], [126.7291, -61.6615]]}
```

The GPlates Web Service server returns a valid GeoJSON MultiPoint geometry that contains the paleo-coordinates of two present-day locations at 140Ma. The paleo-coordinates were calculated according to the plate reconstruction model [Muller2019](https://www.earthbyte.org/muller-et-al-2019-deforming-plate-reconstruction-and-seafloor-age-grids-tectonics/). 

👉 Use curl or wget

- `wget -qO - "https://gws.gplates.org/reconstruct/reconstruct_points/?lons=95,142&lats=54,-33&time=140&model=MULLER2019" `
- `curl "https://gws.gplates.org/reconstruct/reconstruct_points/?lons=95,142&lats=54,-33&time=140&model=MULLER2019" `

👉 Use GPlates Web Service Python Client/Proxy

See the examples at <https://github.com/michaelchin/gwspy/blob/main/README.md>

👉 Setup your own server

**📌For better performance and data security, you may want to setup your own servers.**

Start your own GWS server may be as simple as `docker run -d --rm -p 18000:80 gplates/gws`.

See [docker/README.md](docker/README.md) for the step-by-step instructions.

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

## Servers

The main server is provided by [NCI](https://nci.org.au/) under AuScope scheme.

- https://gws.gplates.org
- https://gws1.gplates.org
- https://gws2.gplates.org


