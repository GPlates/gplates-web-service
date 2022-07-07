#!/usr/bin/env bash

URL_BASE=http://localhost:18000

curl --fail -s -o /dev/null "${URL_BASE}/raster/query?lon=99.50&lat=-40.24&raster_name=age_grid_geek_2007" || printf "FAILED! raster query"

printf "PASSED! raster query\n"

curl --fail -s -o /dev/null "${URL_BASE}/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012" || printf "FAILED! reconstruct_points"

printf "PASSED! reconstruct_points\n"

curl --fail -s -o /dev/null "${URL_BASE}/reconstruct/coastlines/?&time=140&model=SETON2012" || printf "FAILED! coastlines"

printf "PASSED! coastlines\n"