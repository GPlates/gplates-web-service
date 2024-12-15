#!/usr/bin/env python3

import json

import requests

# You need to `pip install requests` to run this example
# This example will get present-day locations from http://paleobiodb.org/ and then use GWS to get their paleo-coordinates.
# The results will be saved into two files in geojson format.
# feature_collection_retrieved_from_paleobiodb.json - the feature collection retrieved from http://paleobiodb.org/
# paleobiodb_feature_collection_reconstructed_by_gws.json - the feature collection reconstructed by GWS


# SERVER_URL = "http://127.0.0.1:18000"
SERVER_URL = "https://gws.gplates.org"

# the number of unique locations from http://paleobiodb.org/
# for demonstration purse, we only use 10 unique locations to explain the idea
NUMBER_OF_LOCATIONS = 10

# the number of records retrieved from http://paleobiodb.org/
# this number is used to limit the size of data returned from http://paleobiodb.org/
# you may use "NUMBER_OF_RECORDS = all" to get all records (the size of returned data may be large)
NUMBER_OF_RECORDS = 100

# the interval ID, contact http://paleobiodb.org/ for the meaning of this ID
INTERVAL_ID = 43


def main():
    # retrieve data from paleobiodb.org
    r = requests.get(
        f"http://paleobiodb.org/data1.1/occs/list.json?limit={NUMBER_OF_RECORDS}&interval_id={INTERVAL_ID}&show=coords,attr,loc,prot,time,strat,stratext,lith,lithext,geo,rem,ent,entname,crmod&showsource",
    )  # use limit=all to return all records. In this example, we use limit={NUMBER_OF_RECORDS} to limit the number of records.

    pbdb = json.loads(r.text)

    print("The keys in the paleobiodb data: ", pbdb.keys())
    print(
        f"There is/are {len(pbdb['records'])} record(s) in the paleobiodb return data."
    )
    # print("The first record in the paleobiodb data: ")
    # print(pbdb["records"][0])

    # being used to keep tracking the locations which have been added
    coordinates_have_seen = []

    # build the geojson FeatureCollection
    # the FeatureCollection will be sent to GWS for plate tectonic reconstruction
    fc = {"type": "FeatureCollection"}
    fc["features"] = []
    for i, record in enumerate(pbdb["records"]):
        coord_string = f"{record['lng']}, {record['lat']}"
        if coord_string in coordinates_have_seen:
            continue  # the coordinates have been added into the feature collection before. ignore this time
        else:
            coordinates_have_seen.append(coord_string)

        feature = {"type": "Feature"}
        feature["geometry"] = {}
        feature["geometry"]["type"] = "Point"
        feature["geometry"]["coordinates"] = [
            float(record["lng"]),
            float(record["lat"]),
        ]
        feature["properties"] = {}
        feature["properties"]["oid"] = record["oid"]
        fc["features"].append(feature)
        print(
            f"oid: {record['oid']}, present-day coordinates: [{record['lng']}, {record['lat']}]"
        )
        if len(coordinates_have_seen) >= NUMBER_OF_LOCATIONS:
            break
    data = {"feature_collection": json.dumps(fc)}

    with open("feature_collection_retrieved_from_paleobiodb.json", "w+") as f:
        f.write(json.dumps(fc, indent=4))

    data["keep_properties"] = True
    data["time"] = 120.0  # reconstruct coordinates to 120Ma

    # reconstruct the geojson FeatureCollection
    r = requests.post(
        SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
        data=data,
        verify=True,
    )

    # save the reconstructed coordinates in geojson format
    with open("paleobiodb_feature_collection_reconstructed_by_gws.json", "w+") as f:
        f.write(json.dumps(json.loads(r.text), indent=4))

    print()
    for f in json.loads(r.text)["features"]:
        print(
            f"oid: {f['properties']['oid']}, paleo-coordinates: {f['geometry']['coordinates']}"
        )


if __name__ == "__main__":
    main()
