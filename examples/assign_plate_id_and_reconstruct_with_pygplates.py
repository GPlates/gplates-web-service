# open this script in vs code
# connect to gplates web service docker container
# run it inside vs code
import os
from pathlib import Path

import pygplates

script_path = os.path.dirname(os.path.realpath(__file__))
# print(script_path)
output_path = f"{script_path}/output"
Path(output_path).mkdir(parents=True, exist_ok=True)

static_polygons_filename = (
    f"{script_path}/../django/GWS/DATA/MODELS/SETON2012/"
    + "Seton_etal_ESR2012_StaticPolygons_2012.1.gpmlz"
)

coastlines_filename = (
    f"{script_path}/../django/GWS/DATA/MODELS/SETON2012/coastlines_low_res/"
    + "Seton_etal_ESR2012_Coastlines_2012.shp"
)

rotation_model = pygplates.RotationModel(
    f"{script_path}/../django/GWS/DATA/MODELS/SETON2012/Seton_etal_ESR2012_2012.1.rot"
)

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

print("Done!")
