#/bin/bash

latitude=34
longitude=80
time=120
model=default

## Need to figure out how to create a list of point, comma-separated, from whatever the input is likely to be

# print the query to check it looks correct
echo 'http://portal.gplates.org/service/reconstruct_points/?points='$latitude','$longitude'&time='$time'&model='$model

# get the contents of the request in a json file
curl --proxy '' 'http://portal.gplates.org/service/reconstruct_points/?points='$latitude','$longitude'&time='$time'&model='$model > reconstructed_coordinates.json
head reconstructed_coordinates.json

# this method uses python to parse the json directly and give you back the reconstructed coordinates
curl --proxy '' 'http://portal.gplates.org/service/reconstruct_points/?points='$latitude','$longitude'&time='$time'&model='$model | \
    python -c "import sys, json; print json.load(sys.stdin)['coordinates']"


