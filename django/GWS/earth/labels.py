import io
import json
import math
import pygplates
from django.conf import settings
import matplotlib.pyplot as plt
from django.http import HttpResponse, HttpResponseBadRequest

from utils.round_float import round_floats
from utils.model_utils import get_reconstruction_model_dict


def read_labels():
    """return a list of labels

    [
        {
            "label": label,
            "lat": lat,
            "lon": lon,
            "fromtime": from_time,
            "totime": to_time,
        }
    ]

    """
    labels = []
    with open(f"{settings.EARTH_STORE_DIR}/labels.csv", "rt") as csv_fp:
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
    return labels


def get_labels(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Only GET request is supported!")

    try:
        time = float(request.GET.get("time", 0))
    except:
        print("Invalid time parameter, use time 0.")
        time = 0

    model = request.GET.get("model", settings.MODEL_DEFAULT)

    model_dict = get_reconstruction_model_dict(model)

    rotation_model = pygplates.RotationModel(
        [
            f"{settings.MODEL_STORE_DIR}/{model}/{rot_file}"
            for rot_file in model_dict["RotationFile"]
        ]
    )

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
            rlons, rlats = gpts.reconstruct(time, return_array=True)
        else:
            rlons = []
            rlats = []
        assert len(lats) == len(lons)
        assert len(rlons) == len(lons)
        assert len(rlats) == len(lats)

        # save as json
        data_str = json.dumps(oceans + list(zip(names, rlats, rlons)), indent=4)
        with open(f"output/{model_name}/json/{time}.json", "w") as outfile:
            outfile.write(data_str)

    response = HttpResponse(
        json.dumps(round_floats(ret)), content_type="application/json"
    )

    # TODO:
    # The "*" makes the service wide open to anyone. We should implement access control when time comes.
    response["Access-Control-Allow-Origin"] = "*"
    return response
