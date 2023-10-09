import pygplates
from django.conf import settings
from plate_model_manager import PlateModel, PlateModelManager


def get_rotation_files(model):
    """return a list of rotation files"""
    plate_model = PlateModel(model, data_dir=settings.MODEL_REPO_DIR, readonly=True)
    return plate_model.get_rotation_model()


def get_rotation_model(model):
    """return a rotation model given the model name

    :param model: model name

    :returns: a pygplates.RotationModel object

    """
    rotation_files = get_rotation_files(model)

    if not rotation_files:
        raise UnrecognizedModel(f'The "model" ({model}) cannot be recognized.')

    return pygplates.RotationModel(rotation_files)


def get_static_polygons_filenames(model):
    """return static polygons filenames

    :param model: model name

    """
    plate_model = PlateModel(model, data_dir=settings.MODEL_REPO_DIR, readonly=True)

    static_polygon_files = plate_model.get_static_polygons()

    if not static_polygon_files:
        raise UnrecognizedModel(f'The "model" ({model}) cannot be recognized.')
    return static_polygon_files


def get_static_polygons(model):
    """return a pygplates.FeatureCollection of static polygons"""
    files = get_static_polygons_filenames(model)
    features = []
    for f in files:
        fc = pygplates.FeatureCollection(f)
        features.extend(fc)
    return pygplates.FeatureCollection(features)


def get_layer(model, layer_name):
    """return a pygplates.FeatureCollection of the layer

    :param model: model name
    :param layer_name: layer name

    """
    plate_model = PlateModel(model, data_dir=settings.MODEL_REPO_DIR, readonly=True)
    files = plate_model.get_layer(layer_name)
    features = []
    for f in files:
        fc = pygplates.FeatureCollection(f)
        features.extend(fc)
    return pygplates.FeatureCollection(features)


def get_topologies(model):
    """return a list of topology files"""
    plate_model = PlateModel(model, data_dir=settings.MODEL_REPO_DIR, readonly=True)
    return plate_model.get_topologies()


def get_model_name_list(folder):
    """get a list of model names from the given folder."""

    return PlateModelManager.get_local_available_model_names(folder)


def is_time_valid_for_model(model_name, time):
    """returns True if the time is within the valid time of specified model"""

    plate_model = PlateModel(
        model_name, data_dir=settings.MODEL_REPO_DIR, readonly=True
    )

    return (
        float(time) <= plate_model.get_big_time()
        and float(time) >= plate_model.get_small_time()
    )


def get_layer_names(model_name):
    """return all the layers in a model"""
    plate_model = PlateModel(
        model_name, data_dir=settings.MODEL_REPO_DIR, readonly=True
    )
    return plate_model.get_avail_layers()


def get_model_cfg(model_name):
    """return the configuration of a model"""
    plate_model = PlateModel(
        model_name, data_dir=settings.MODEL_REPO_DIR, readonly=True
    )
    return plate_model.get_cfg()


class UnrecognizedModel(Exception):
    pass
