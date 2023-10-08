import json
import os

import requests

from .plate_model import PlateModel


class PlateModelManager:
    """load a models.json file and manage plate models
    see an example models.json file at PlateModelManager.get_default_repo_url()

    """

    def __init__(self, model_manifest=None):
        """constructor

        :param model_manifest: the path to a models.json file

        """
        if not model_manifest:
            self.model_manifest = PlateModelManager.get_default_repo_url()
        else:
            self.model_manifest = model_manifest
        self.models = None

        # check if the model manifest file is a local file
        if os.path.isfile(self.model_manifest):
            with open(self.model_manifest) as f:
                self.models = json.load(f)
        elif self.model_manifest.startswith(
            "http://"
        ) or self.model_manifest.startswith("https://"):
            # try the http(s) url
            try:
                r = requests.get(self.model_manifest)
                self.models = r.json()

            except requests.exceptions.ConnectionError:
                raise Exception(
                    f"Unable to fetch {self.model_manifest}. "
                    + "No network connection or invalid URL!"
                )
        else:
            raise Exception(
                f"The model_manifest '{self.model_manifest}' should be either a local file path or a http(s) URL."
            )

    def get_model(self, model_name: str):
        """return a PlateModel object by model_name

        :param model_name: model name

        :returns: a PlateModel object or none if model name is no good

        """
        model_name = model_name.lower()
        if model_name in self.models:
            return PlateModel(model_name, model_cfg=self.models[model_name])
        else:
            print(f"Model {model_name} is not available.")
            return None

    def get_available_model_names(self):
        """return the names of available models as a list"""
        return [name for name in self.models]

    @staticmethod
    def get_local_available_model_names(local_dir):
        """list all model names in a local folder"""
        models = []
        for file in os.listdir(local_dir):
            d = os.path.join(local_dir, file)
            if os.path.isdir(d) and os.path.isfile(f"{d}/.metadata.json"):
                models.append(file)
        return models

    @staticmethod
    def get_default_repo_url():
        return "https://repo.gplates.org/webdav/pmm/models.json"

    def download_all_models(self, data_dir="./"):
        model_names = self.get_available_model_names()
        for name in model_names:
            print(f"download {name}")
            model = self.get_model(name)
            model.set_data_dir(data_dir)
            model.download_all_layers()
