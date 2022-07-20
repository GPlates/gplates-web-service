#!/usr/bin/env bash

# check if the GWS_SERVER_URL has been set.
if [[ -z "${GWS_SERVER_URL}" ]]; then
  GWS_SERVER_URL=http://localhost:18000
  printf "Using server URL set in test-server.sh ${GWS_SERVER_URL}\n"
else
  printf "Using server URL in environment variable ${GWS_SERVER_URL}\n"
fi 

curl --fail -s -o /dev/null "${GWS_SERVER_URL}/raster/query?lon=99.50&lat=-40.24&raster_name=age_grid_geek_2007" || printf "FAILED! raster query"

printf "PASSED! raster query\n"

curl --fail -s -o /dev/null "${GWS_SERVER_URL}/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012" || printf "FAILED! reconstruct_points"

printf "PASSED! reconstruct_points\n"

curl --fail -s -o /dev/null "${GWS_SERVER_URL}/reconstruct/coastlines/?&time=140&model=SETON2012" || printf "FAILED! coastlines"

printf "PASSED! coastlines\n"

python3 $(dirname "$0")/test.py