import pygplates
from django.conf import settings
from plate_model_manager import PlateModel, PlateModelManager

from .downsample_polygons import downsample_polygons

FEATURE_COLLECTION_CACHE = {
    "Rotations": {},
    "Coastlines": {},
    "StaticPolygons": {},
    "ContinentalPolygons": {},
    "Topologies": {},
    "CoastlinesLow": {},
}
ROTATION_FC = FEATURE_COLLECTION_CACHE["Rotations"]
COASTLINES_FC = FEATURE_COLLECTION_CACHE["Coastlines"]
STATIC_POLYGONS_FC = FEATURE_COLLECTION_CACHE["StaticPolygons"]
TOPOLOGIES_FC = FEATURE_COLLECTION_CACHE["Topologies"]
CONTINENTAL_POLYGONS_FC = FEATURE_COLLECTION_CACHE["ContinentalPolygons"]
COASTLINES_LOW_FC = FEATURE_COLLECTION_CACHE["CoastlinesLow"]

PlATE_MODEL_CACHE = {}


def get_coastline_low(model_name):
    if model_name in COASTLINES_LOW_FC:
        return COASTLINES_LOW_FC[model_name]
    else:
        fc = get_layer(model_name, "Coastlines")
        fc_low = downsample_polygons(fc)
        COASTLINES_LOW_FC[model_name] = fc_low
        return fc_low


def get_rotation_files(model):
    """return a list of rotation files"""
    plate_model = get_plate_model(model)
    if not plate_model:
        raise UnrecognizedModel(f'The "model" ({model}) cannot be recognized.')
    return plate_model.get_rotation_model()


def get_rotation_model(model):
    """return a rotation model given the model name

    :param model: model name

    :returns: a pygplates.RotationModel object

    """
    if model in ROTATION_FC:
        return ROTATION_FC[model]
    else:
        rotation_files = get_rotation_files(model)
        m = pygplates.RotationModel(rotation_files)
        ROTATION_FC[model] = m
        return m


def get_static_polygons(model):
    """return a pygplates.FeatureCollection of static polygons"""
    return get_layer(model, "StaticPolygons")


def get_continental_polygons(model):
    """return a pygplates.FeatureCollection of continental polygons"""
    return get_layer(model, "ContinentalPolygons")


def get_layer(model, layer_name):
    """return a pygplates.FeatureCollection of the layer

    :param model: model name
    :param layer_name: layer name

    """
    plate_model = get_plate_model(model)
    if not plate_model:
        raise UnrecognizedModel(f'The "model" ({model}) cannot be recognized.')

    files = plate_model.get_layer(layer_name)
    if not files:
        print(f"Warning: layer({layer_name}) not found for model({model})")

    if layer_name not in FEATURE_COLLECTION_CACHE:
        FEATURE_COLLECTION_CACHE[layer_name] = {}

    if model in FEATURE_COLLECTION_CACHE[layer_name]:
        return FEATURE_COLLECTION_CACHE[layer_name][model]
    else:
        features = []
        for f in files:
            fc = pygplates.FeatureCollection(f)
            features.extend(fc)
        m = pygplates.FeatureCollection(features)
        FEATURE_COLLECTION_CACHE[layer_name][model] = m
        return m


def get_coastlines(model):
    """return a coastlines pygplates.FeatureCollection"""
    return get_layer(model, "Coastlines")


def get_topologies(model):
    """return a topology pygplates.FeatureCollection"""
    return get_layer(model, "Topologies")


def get_model_name_list(folder):
    """get a list of model names from the given folder."""

    return PlateModelManager.get_local_available_model_names(folder)


def is_time_valid_for_model(model_name, time):
    """returns True if the time is within the valid time of the specified model"""

    plate_model = get_plate_model(model_name)
    big_time = plate_model.get_big_time()
    small_time = plate_model.get_small_time()
    assert big_time > small_time
    timef = float(time)
    return timef <= big_time and timef >= small_time


def get_layer_names(model_name):
    """return all the layers in a model"""
    plate_model = get_plate_model(model_name)
    return plate_model.get_avail_layers()


def get_model_cfg(model_name):
    """return the configuration of a model"""
    plate_model = get_plate_model(model_name)
    return plate_model.get_cfg()


def get_valid_time(model_name):
    """return the valid time of a model"""
    plate_model = get_plate_model(model_name)
    return {
        "big_time": plate_model.get_big_time(),
        "small_time": plate_model.get_small_time(),
    }


def get_plate_model(model_name):
    """return a PlateModel object"""
    if model_name not in PlATE_MODEL_CACHE:
        plate_model = PlateModel(
            model_name, data_dir=settings.MODEL_REPO_DIR, readonly=True
        )
        PlATE_MODEL_CACHE[model_name] = plate_model

    return PlATE_MODEL_CACHE[model_name]


class UnrecognizedModel(Exception):
    pass
