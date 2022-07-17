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

shp_path = (
    f"{script_path}/../django/GWS/DATA/MODELS/SETON2012/coastlines_low_res/"
    + "Seton_etal_ESR2012_Coastlines_2012.shp"
)

rotation_model = pygplates.RotationModel(
    f"{script_path}/../django/GWS/DATA/MODELS/SETON2012/Seton_etal_ESR2012_2012.1.rot"
)
time = 100
pygplates.reconstruct(
    shp_path, rotation_model, f"{output_path}/reconstructed_{time}Ma.shp", time
)

# pygplates.reconstruct(
#    f"{script_path}/Seton_etal_ESR2012_Coastlines_2012.shp",
#    rotation_model,
#    f"{output_path}/reconstructed_{time}Ma.shp",
#    time,
# )
print("done!")
