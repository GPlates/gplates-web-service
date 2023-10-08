#!/usr/bin/env python3
# use gplately conda env to run
# conda create -n my-env gplately
import os
from pathlib import Path

import pygplates
from plate_model_manager import PlateModelManager


def main():
    script_path = os.path.dirname(os.path.realpath(__file__))
    # print(script_path)
    output_path = f"{script_path}/output"
    Path(output_path).mkdir(parents=True, exist_ok=True)

    mgr = PlateModelManager()
    model = mgr.get_model("SETON2012")

    static_polygons_filename = model.get_static_polygons()
    coastlines_filename = model.get_coastlines()
    rotation_model = pygplates.RotationModel(model.get_rotation_model())

    features = pygplates.partition_into_plates(
        static_polygons_filename,
        rotation_model,
        coastlines_filename,
        partition_method=pygplates.PartitionMethod.most_overlapping_plate,
        properties_to_copy=[
            pygplates.PartitionProperty.reconstruction_plate_id,
            pygplates.PartitionProperty.valid_time_period,
        ],
    )

    feature_collection = pygplates.FeatureCollection(features)
    feature_collection.write(f"{output_path}/plate-id-assigned.gpml")

    # reconstruct the partitioned features
    time = 100
    pygplates.reconstruct(
        feature_collection,
        rotation_model,
        f"{output_path}/reconstructed_{time}Ma.shp",
        time,
    )

    print(f"Done! The result has been saved in {output_path}.")


if __name__ == "__main__":
    main()
