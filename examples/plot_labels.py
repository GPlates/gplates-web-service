#!/usr/bin/env python3
# use gplately conda env to run
# conda create -n my-env gplately
import os
from pathlib import Path

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import requests
from shapely.geometry import shape

SERVER_URL = os.getenv("GWS_SERVER_URL")
if not SERVER_URL:
    SERVER_URL = "https://gws.gplates.org"
    print(f"Using server URL in script {SERVER_URL}")
else:
    print(f"Using server URL in environment variable {SERVER_URL}")

script_path = os.path.dirname(os.path.realpath(__file__))
output_path = f"{script_path}/output/labels"
Path(output_path).mkdir(parents=True, exist_ok=True)


def plot_labels(time, model):
    fig = plt.figure(figsize=(16, 12), dpi=540)
    ax = plt.axes(projection=ccrs.Robinson())

    ax.set_global()
    ax.gridlines()

    r = requests.get(f"{SERVER_URL}/reconstruct/coastlines/?model={model}&time={time}")
    feature_collection = r.json()["features"]
    geoms = [shape(feature["geometry"]).buffer(0) for feature in feature_collection]

    ax.add_geometries(
        geoms, crs=ccrs.PlateCarree(), facecolor="lime", edgecolor="black", alpha=0.8
    )

    r = requests.get(f"{SERVER_URL}/earth/get_labels?time={time}&model={model}")
    if r.status_code != 200:
        raise Exception("Failed to get coastlines!")
    labels = r.json()
    names = []
    lons = []
    lats = []
    for label in labels:
        names.append(label[0])
        lats.append(label[1])
        lons.append(label[2])
        plt.text(
            label[2],
            label[1],
            label[0],
            va="baseline",
            family="monospace",
            weight="bold",
            color="red",
            transform=ccrs.PlateCarree(),
        )

    plt.plot(lons, lats, "o", transform=ccrs.PlateCarree())

    # save the figure without frame so that the image can be used to project onto a globe
    fig.savefig(f"{output_path}/labels-{time}-Ma.png", dpi=120)
    plt.close(fig)

    print(f"Done! The labels-{time}-Ma.png has been saved in {output_path}.")


if __name__ == "__main__":
    model = "MERDITH2021"
    for time in range(0, 1001, 10):
        plot_labels(time, model)
