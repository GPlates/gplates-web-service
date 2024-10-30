#!/usr/bin/env bash

# check if the GWS_SERVER_URL has been set.
if [[ -z "${GWS_SERVER_URL}" ]]; then
  #GWS_SERVER_URL=http://localhost:18000
  GWS_SERVER_URL=https://gws.gplates.org
  printf "Using server URL set in test-server.sh ${GWS_SERVER_URL}\n"
else
  printf "Using server URL in environment variable ${GWS_SERVER_URL}\n"
fi 

curl --fail -s -o /dev/null "${GWS_SERVER_URL}/raster/query?lon=99.50&lat=-40.24&raster_name=crustal_thickness" || { printf "FAILED! raster query\n"; exit 1; } 

printf "PASSED! raster query\n"

curl --fail -s -o /dev/null "${GWS_SERVER_URL}/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012" || { printf "FAILED! reconstruct_points\n"; exit 1; }

printf "PASSED! reconstruct_points\n"

curl --fail -s -o /dev/null "${GWS_SERVER_URL}/reconstruct/coastlines/?&time=140&model=SETON2012" ||  { printf "FAILED! coastlines\n"; exit 1; }

printf "PASSED! coastlines\n"
