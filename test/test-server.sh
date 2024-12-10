#!/usr/bin/env bash

# check if the GWS_SERVER_URL has been set.
if [[ -z "${GWS_SERVER_URL}" ]]; then
  GWS_SERVER_URL=http://localhost:18000
  #GWS_SERVER_URL=http://gws.gplates.org
  printf "Using default server URL in test-server.sh ${GWS_SERVER_URL}\n"
else
  printf "Using server URL in environment variable GWS_SERVER_URL ${GWS_SERVER_URL}\n"
fi 

GWS_TEST_VALIDATE_WITH_PYGPLATES=False
GWS_TEST_DB_QUERY=False

cd $(dirname "$0")/testcases
python3 -m unittest -vv

