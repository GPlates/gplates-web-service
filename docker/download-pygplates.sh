#!/bin/bash

ARCH=$(dpkg --print-architecture)
if [ $ARCH = "arm64" ]
then
    wget https://www.earthbyte.org/download/9316/ -O /pygplates_0.36.0_py310_ubuntu-22.04.deb
elif [ $ARCH = "amd64" ]
then
     wget https://www.earthbyte.org/download/9079/ -O /pygplates_0.36.0_py310_ubuntu-22.04.deb
else
    echo "Unknown architecture $ARCH"
    exit 1
fi
