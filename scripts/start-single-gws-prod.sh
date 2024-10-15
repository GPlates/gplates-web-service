#!/bin/bash

echo $1

HCMD='curl --fail -s "http://localhost:80/reconstruct/reconstruct_points/?points=95,54,142,-33&time=140" || exit 1'
PORT=18000

if [ -z "$1" ]
then
  docker run -d --name gplates_web_service -p $PORT:80 --restart always --health-cmd='$HCMD' gplates/gws
else
  docker run -d --name gplates_web_service -v $1:/gws -p $PORT:80 --restart always --health-cmd='$HCMD' gplates/gws
fi

