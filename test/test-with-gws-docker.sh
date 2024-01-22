#!/usr/bin/env bash

docker run -it --rm -v`pwd`:/workspace --network host gplates/gws /workspace/"$1"