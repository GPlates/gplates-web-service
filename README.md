# GPlates Web Service

![Test](https://github.com/gplates/gplates-web-service/actions/workflows/test.yml/badge.svg)
![Build Docker](https://github.com/gplates/gplates-web-service/actions/workflows/build-and-push-docker.yml/badge.svg)
![Release Test](https://github.com/gplates/gplates-web-service/actions/workflows/release-test.yml/badge.svg)

The **🔥GPlates Web Service🔥** is a part of the on-going GPlates project funded by [AuScope](https://www.auscope.org.au/). The web service is built upon [pyGPlates](https://www.gplates.org/docs/pygplates/index.html) and allows users to utilize the pyGPlates functionalities without the need of installing pyGPlates locally. Users send HTTP requests to https://gws.gplates.org or On-Prem server, and then the server will process the requests and send the results back. The web service provides access to pyGPlates functionalities across multiple programming languages and operating systems.

The GPlates Web Service is created and maintained by [EarthByte](https://www.earthbyte.org) group at the [University of Sydney](https://www.sydney.edu.au/).

Please give us a ⭐**star**⭐ to show your support for our development team. Thank you very much!

![Main Animation](https://github.com/GPlates/gplates-web-service/raw/master/doc/content/images/gws-location-reconstruction.gif)

## 🤔 Why GPlates Web Service

- easy to use -- it can be as easy as opening a URL in a web browser or a one-line curl command in a terminal
- cross-platform and programming language independent -- the service can be used in various programming languages and on various operating systems
- scalability -- distribute workload among servers, cluster, grid or Cloud to improve throughput and support concurrent usage
- automated plate reconstruction model management -- provide a wide range of plate reconstruction models out of the box
- software deployment and upgrade -- the software installation and upgrade are much easier than local software

## 🚀 Quick start

👉 Use the GPlates Web Service in a web browser

- Step 1: click this [link](https://gws.gplates.org/reconstruct/reconstruct_points/?lons=95,142&lats=54,-33&time=140&model=ZAHIROVIC2022) 
- Step 2: the paleo-coordinates will show in the web browser in GeoJSON format (see the explanation below).

```
{"type": "MultiPoint", "coordinates": [[59.3469, 60.9242], [124.7549, -59.069]]}
```

The server returns a valid GeoJSON MultiPoint geometry containing the paleo-coordinates of two present-day locations ([95,54] and [142,-33]) at 140 Ma. The paleo-coordinates are calculated using the plate reconstruction model [ZAHIROVIC2022](https://gwsdoc.gplates.org/models#zahirovic2022). 

👉 Use curl or wget

```
wget -qO - "https://gws.gplates.org/reconstruct/reconstruct_points/?lons=95,142&lats=54,-33&time=140&model=ZAHIROVIC2022" 
```

```
curl "https://gws.gplates.org/reconstruct/reconstruct_points/?lons=95,142&lats=54,-33&time=140&model=ZAHIROVIC2022" 
```

👉 Use GPlates Web Service Python Wrapper(gwspy)

The examples of using the web service in Python can be found at [here](https://github.com/michaelchin/gwspy/blob/main/README.md).

👉 Use GPlates Web Service in R

The [rgplates](https://gplates.github.io/rgplates/) is a good example of using GPlates Web Service in R programming language. 

👉 Use GPlates Web Service in JavaScript

The [gplates-js](https://github.com/michaelchin/gplates-js) is an experimental project of using GPlates Web Service in JavaScript programming language.

👉 Setup your own server

You are welcome to use our servers. But for better performance and data security, you might want to set up the service on your own server/personal computer.

Start your own GWS server is as simple as the one-line command below. You need [Docker](https://www.docker.com/get-started/) to run this command.

```
docker run -d --rm -p 18000:80 gplates/gws
```

See [docker/README.md](docker/README.md) for the step-by-step instructions.

## 📂 Contents

- **django** -- source files for the backend

- **docker** -- files for building Docker image

- **doc** -- source files for the online documentation website 

- **examples** -- examples of the usage of this web service

- **test** -- source code for testing

- **scripts** -- some miscellaneous supporting scripts

- **data** -- symbolic link to the folder containing the data files


## 🐳 Docker

Click this 👉[link](docker/README.md)👈 to see details about using Docker in the development/production environment.

## 📚 Documentation

- [GWS Documentation Website](https://gwsdoc.gplates.org/)

- [Swagger UI](https://gws.gplates.org/swagger-ui/)

- [OpenAPI Schema](https://gws.gplates.org/openapi)

- [Usage Examples](https://gwsdoc.gplates.org/examples)

Some more examples of accessing the service from different languages (R, MATLAB, bash/GMT, Python) can be found at https://github.com/siwill22/gws-examples.

## 📮 Contact

👉 [Contact EarthByte](https://www.earthbyte.org/contact-us-3/)

## 📝 License

The GPlates Web Service is free software (also known as open-source software), licensed for distribution under the GNU [General Public License (GPL) Version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html). Contact [EarthByte](https://www.earthbyte.org/contact-us-3/) group regarding the details of the software licensing.

## 🖥️ Servers

The main server is provided by [NCI Cloud](https://nci.org.au/) under AuScope scheme. Two backup servers are provided by NCI and EarthByte group.

- https://gws.gplates.org (main server)
- https://gws1.gplates.org (NCI backup server)
- https://gws2.gplates.org (EarthByte backup server)


