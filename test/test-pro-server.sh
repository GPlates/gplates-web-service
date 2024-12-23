#!/usr/bin/env bash

export GWS_SERVER_URL=https://gws.gplates.org

export GWS_TEST_VALIDATE_WITH_PYGPLATES=True
export GWS_TEST_DB_QUERY=True

$(dirname "$0")/test-server.sh
