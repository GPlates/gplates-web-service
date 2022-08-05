import json
import os

import pygplates
from django.conf import settings

#
# return a dictionary of all available reconstruction models
#
def get_reconstruction_model_dict(MODEL_NAME):
    # Model registry
    with open(f"{settings.BASE_DIR}/DATA/MODELS.json") as f:
        models = json.load(f)
        if MODEL_NAME in models:
            return models[MODEL_NAME]
        else:
            return None


#
# return a rotation model given the model name
#
def get_rotation_model(model):
    model_dict = get_reconstruction_model_dict(model)

    if not model_dict:
        raise UnrecognizedModel('The "model" ({0}) cannot be recognized.'.format(model))

    return pygplates.RotationModel(
        [
            f"{settings.MODEL_STORE_DIR}/{model}/{rot_file}"
            for rot_file in model_dict["RotationFile"]
        ]
    )


#
# return static polygons filename
#
def get_static_polygons_filename(model):
    model_dict = get_reconstruction_model_dict(model)

    if not model_dict:
        raise UnrecognizedModel('The "model" ({0}) cannot be recognized.'.format(model))
    return f'{settings.MODEL_STORE_DIR}/{model}/{model_dict["StaticPolygons"]}'


def get_model_name_list(MODEL_STORE, include_hidden=True):
    # get a list of models from the model store.
    # if 'include_hidden' is set to False, only the manually defined list of 'validated'
    # models is returned. Otherwise, assume every directory within the model store is a valid model

    if include_hidden:
        return [
            o
            for o in os.listdir(MODEL_STORE)
            if os.path.isdir(os.path.join(MODEL_STORE, o))
        ]
    else:
        with open(f"{settings.BASE_DIR}/DATA/MODELS.json") as f:
            models = json.load(f)
            return models.keys()


def is_time_valid_model(model_dict, time):
    # returns True if the time is within the valid time of specified model
    return (
        float(time) <= model_dict["ValidTimeRange"][0]
        and float(time) >= model_dict["ValidTimeRange"][1]
    )


class UnrecognizedModel(Exception):
    pass
