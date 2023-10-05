#!/usr/bin/env python3
# use gplately conda env to run
# conda create -n my-env gplately
import json, requests, os
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
import cartopy
import cartopy.crs as ccrs
from pathlib import Path
from shapely.geometry import shape, GeometryCollection

SERVER_URL = os.getenv("GWS_SERVER_URL")
if not SERVER_URL:
    SERVER_URL = "https://gws.gplates.org"
    print(f"Using server URL in script {SERVER_URL}")
else:
    print(f"Using server URL in environment variable {SERVER_URL}")

fig = plt.figure(figsize=(16, 12), dpi=540)
ax = plt.axes(projection=ccrs.Robinson())

ax.set_global()
ax.gridlines()

r = requests.get(f"{SERVER_URL}/reconstruct/coastlines/")
feature_collection = r.json()["features"]
print(type(feature_collection))
geoms = [shape(feature["geometry"]).buffer(0) for feature in feature_collection]


# ax.stock_img()

# print(geoms)
ax.add_geometries(
    geoms, crs=ccrs.PlateCarree(), facecolor="lime", edgecolor="black", alpha=0.8
)

r = requests.get(f"http://localhost:18000/earth/get_labels?time=0&model=merdith2021")
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

script_path = os.path.dirname(os.path.realpath(__file__))
output_path = f"{script_path}/output"
Path(output_path).mkdir(parents=True, exist_ok=True)
# save the figure without frame so that the image can be used to project onto a globe
fig.savefig(f"{output_path}/labels.png", dpi=120)
plt.close(fig)

print(f"Done! The result has been saved in {output_path}.")
