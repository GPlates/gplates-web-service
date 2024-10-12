#!/usr/bin/env bash

# check if the GWS_SERVER_URL has been set.
if [[ -z "${GWS_SERVER_URL}" ]]; then
  #GWS_SERVER_URL=http://localhost:18000
  GWS_SERVER_URL=https://gws.gplates.org
  printf "Using server URL set in test-server.sh ${GWS_SERVER_URL}\n"
else
  printf "Using server URL in environment variable ${GWS_SERVER_URL}\n"
fi 

for i in {0..100}
do
    echo $i
    curl "${GWS_SERVER_URL}/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012" 
done
