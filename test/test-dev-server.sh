#!/usr/bin/env bash

export GWS_SERVER_URL=http://localhost:18000

GWS_TEST_VALIDATE_WITH_PYGPLATES=True
GWS_TEST_DB_QUERY=True

$(dirname "$0")/test-server.sh
