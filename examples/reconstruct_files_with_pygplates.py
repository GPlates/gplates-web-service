#!/usr/bin/env python3
# use gplately conda env to run
# conda create -n my-env gplately
import os
from pathlib import Path

import pygplates
import requests
from plate_model_manager import PlateModelManager


def main():
    script_path = os.path.dirname(os.path.realpath(__file__))
    # print(script_path)
    output_path = f"{script_path}/output"
    Path(output_path).mkdir(parents=True, exist_ok=True)

    if not os.path.isfile("Global_EarthByte_GPlates_PresentDay_Coastlines.gpmlz"):
        r = requests.get(
            "https://repo.gplates.org/webdav/mchin/data/Global_EarthByte_GPlates_PresentDay_Coastlines.gpmlz",
            allow_redirects=True,
        )
        open("Global_EarthByte_GPlates_PresentDay_Coastlines.gpmlz", "wb").write(
            r.content
        )

    mgr = PlateModelManager()
    model = mgr.get_model("SETON2012")

    time = 100
    pygplates.reconstruct(
        "Global_EarthByte_GPlates_PresentDay_Coastlines.gpmlz",
        model.get_rotation_model(),
        f"{output_path}/reconstructed_{time}Ma.shp",
        time,
    )

    print(f"Done! The result has been saved to {output_path}.")


if __name__ == "__main__":
    main()
