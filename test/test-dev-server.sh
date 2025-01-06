#!/usr/bin/env bash

export GWS_SERVER_URL=http://localhost:18000

export GWS_TEST_VALIDATE_WITH_PYGPLATES=True
export GWS_TEST_DB_QUERY=False

$(dirname "$0")/test-server.sh
