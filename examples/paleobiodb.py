#!/usr/bin/env python3

import json
from pathlib import Path

import requests

# get present-day locations from http://paleobiodb.org/ and use GWS to get their paleo-coordinates

# SERVER_URL = "http://127.0.0.1:18000"
SERVER_URL = "https://gws.gplates.org"
NUMBER_OF_RECORDS = 10
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

    # build the geojson FeatureCollection
    # the FeatureCollection will be sent to GWS for plate tectonic reconstruction
    fc = {"type": "FeatureCollection"}
    fc["features"] = []
    for i, record in enumerate(pbdb["records"]):
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        feature["geometry"]["type"] = "Point"
        feature["geometry"]["coordinates"] = [record["lng"], record["lat"]]
        feature["properties"] = {}
        feature["properties"]["oid"] = record["oid"]
        fc["features"].append(feature)
        print(
            f"oid: {record['oid']}, present-day coordinates: [{record['lng']}, {record['lat']}]"
        )

    data = {"feature_collection": json.dumps(fc)}

    data["keep_properties"] = True
    data["time"] = 120.0

    # print(data)

    # reconstruct the geojson FeatureCollection
    r = requests.post(
        SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
        data=data,
        verify=True,
    )
    # print(r.text)
    print()
    for f in json.loads(r.text)["features"]:
        print(
            f"oid: {f['properties']['oid']}, paleo-coordinates: {f['geometry']['coordinates']}"
        )


if __name__ == "__main__":
    main()
