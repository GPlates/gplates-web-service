#!/usr/bin/env python

# This file is deprecated due to the redesign of plate labels.
# See https://github.com/GPlates/plate-labels instead

# use gplately and plate_model_manager to run this script
# this script do two things
# 1. assign plate ids for labels (pre-compute/pre-assign plate ids to improve response time)
# 2. reconstruct labels (for label caching)

import json
import os
from pathlib import Path

import gplately
import pygplates
from plate_model_manager import PlateModelManager

model_names = [
    "MULLER2022",
    "MULLER2016",
    "MATTHEWS2016_mantle_ref",
    "MATTHEWS2016_pmag_ref",
    "SETON2012",
    "MERDITH2021",
    "MULLER2019",
]


def main():
    labels = read_labels()
    for model in model_names:
        # print(f"generate labels for {model} ...")
        # gen_labels(model, labels)
        print(f"get label pids for {model} ...")
        get_label_plate_id(model, labels)


def read_labels():
    labels = []
    with open("Lithodat_Labels.csv", "rt") as csv_fp:
        for line in csv_fp:
            items = line.split(",")
            if len(items) < 5:  # ignore when length is wrong
                print(f"ignore invlid line: {line}")
                continue
            try:
                label = items[0]
                lat = float(items[1])
                lon = float(items[2])
                from_time = int(items[3])
                to_time = int(items[4])
            except:
                print(f"ignore invlid line: {line}")
                continue

            labels.append(
                {
                    "label": label,
                    "lat": lat,
                    "lon": lon,
                    "fromtime": from_time,
                    "totime": to_time,
                }
            )
    # print(labels)
    return labels


def gen_labels(model_name, labels):
    model_manager = PlateModelManager()
    model = model_manager.get_model(model_name)
    model.set_data_dir(f"{os.path.dirname(__file__)}/model-repo")

    # print(model.get_static_polygons())

    gplately_model = gplately.PlateReconstruction(
        rotation_model=model.get_rotation_model(),
        topology_features=[],
        static_polygons=model.get_static_polygons(),
    )

    Path(f"output/{model_name}/csv").mkdir(parents=True, exist_ok=True)
    Path(f"output/{model_name}/shapefile").mkdir(parents=True, exist_ok=True)
    Path(f"output/{model_name}/json").mkdir(parents=True, exist_ok=True)

    for time in range(model.get_small_time(), model.get_big_time() + 1):
        names = []
        lons = []
        lats = []
        oceans = []
        for row in labels:
            if row["fromtime"] >= time and row["totime"] <= time:
                label = " ".join(row["label"].split(" "))
                if label.endswith("Ocean"):
                    oceans.append((label, row["lat"], row["lon"]))
                else:
                    names.append(label)
                    lons.append(row["lon"])
                    lats.append(row["lat"])

        # print(lons, lats)
        if len(lons):
            gpts = gplately.Points(gplately_model, lons, lats)
            print(gpts.plate_id)
            rlons, rlats = gpts.reconstruct(time, return_array=True)
        else:
            rlons = []
            rlats = []
        assert len(lats) == len(lons)
        assert len(rlons) == len(lons)
        assert len(rlats) == len(lats)

        # save as csv
        with open(f"output/{model_name}/csv/{time}.csv", "w+") as output_fp:
            output_fp.write("label,lat,lon\n")
            for row in oceans:
                output_fp.write(f"{row[0]},{row[1]},{row[2]}\n")
            for row in zip(names, rlats, rlons):
                output_fp.write(f"{row[0]},{row[1]},{row[2]}\n")

        # save as shapefile
        feature_collection = pygplates.FeatureCollection()
        for row in oceans:
            feature = pygplates.Feature()
            feature.set_name(row[0])
            feature.set_geometry(pygplates.PointOnSphere(row[1], row[2]))
            feature_collection.add(feature)
        for row in zip(names, rlats, rlons):
            feature = pygplates.Feature()
            feature.set_name(row[0])
            feature.set_geometry(pygplates.PointOnSphere(row[1], row[2]))
            feature_collection.add(feature)

        feature_collection.write(f"output/{model_name}/shapefile/{time}.shp")

        # save as json
        data_str = json.dumps(oceans + list(zip(names, rlats, rlons)), indent=4)
        with open(f"output/{model_name}/json/{time}.json", "w") as outfile:
            outfile.write(data_str)


def get_label_plate_id(model_name, labels):
    model_manager = PlateModelManager()
    model = model_manager.get_model(model_name)
    model.set_data_dir(f"{os.path.dirname(__file__)}/model-repo")

    gplately_model = gplately.PlateReconstruction(
        rotation_model=model.get_rotation_model(),
        topology_features=[],
        static_polygons=model.get_static_polygons(),
    )

    pids = []
    lons = []
    lats = []
    for row in labels:
        lons.append(row["lon"])
        lats.append(row["lat"])

    gpts = gplately.Points(gplately_model, lons, lats)
    pids = gpts.plate_id
    assert len(labels) == len(pids)
    # save as csv
    with open(f"output/labels-{model_name.lower()}.csv", "w+") as output_fp:
        output_fp.write("label,lat,lon,fromtime,totime,pid\n")
        for label, pid in zip(labels, pids):
            output_fp.write(
                f"{label['label']},{label['lat']},{label['lon']},{label['fromtime']},{label['totime']},{pid}\n"
            )

    with open(f"output/label-pids-{model_name.lower()}.csv", "w+") as output_fp:
        for pid in pids:
            output_fp.write(f"{pid}\n")


if __name__ == "__main__":
    main()
