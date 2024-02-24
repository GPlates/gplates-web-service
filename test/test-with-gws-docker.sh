#!/usr/bin/env bash

# in the "test" folder
# run ./test-with-gws-docker.sh test-dev-server.sh
# run the testcases in GWS docker image because some of the cases need pygplates.

docker run -it --rm -v`pwd`:/workspace --network host gplates/gws /workspace/"$1"