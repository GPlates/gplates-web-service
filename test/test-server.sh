#!/usr/bin/env bash

# check if the GWS_SERVER_URL has been set.
if [[ -z "${GWS_SERVER_URL}" ]]; then
  GWS_SERVER_URL=http://localhost:18000
  #GWS_SERVER_URL=http://gws.gplates.org
  printf "Using server URL set in test-server.sh ${GWS_SERVER_URL}\n"
else
  printf "Using server URL in environment variable ${GWS_SERVER_URL}\n"
fi 

cd $(dirname "$0")/testcases
python3 -m unittest -vv

