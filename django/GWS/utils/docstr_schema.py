import yaml
from rest_framework.schemas.openapi import AutoSchema

# inspired by https://igeorgiev.eu/python/misc/python-django-rest-framework-openapi-documentation/


class DocstrSchema(AutoSchema):
    """
    Use docstring to generate openAPI schema
    """

    @property
    def docdict(self):
        """
        the dictionary being created from the docstring of the view
        """
        if not hasattr(self, "_docdict"):
            try:
                self._docdict = yaml.safe_load(self.view.__doc__)
            except yaml.scanner.ScannerError:
                self._docdict = {}
        return self._docdict

    def get_components(self, path, method):
        """
        override get_components
        """
        components = super().get_components(path, method)
        new_comps = self.docdict.get("components", {})
        if type(new_comps) is dict:
            components.update(new_comps)

        return components

    def get_operation(self, path, method):
        """
        override get_operation
        """
        operation = super().get_operation(path, method)
        new_op = self.docdict.get(method.lower(), {})

        if type(new_op) is dict:
            operation.update(new_op)
        return operation
