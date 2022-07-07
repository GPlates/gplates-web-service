#!/usr/bin/env bash

curl "http://localhost:18000/raster/query?lon=99.50&lat=-40.24&raster_name=age_grid_geek_2007"

printf "\n"

curl "http://localhost:18000/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140&model=SETON2012"

printf "\n"