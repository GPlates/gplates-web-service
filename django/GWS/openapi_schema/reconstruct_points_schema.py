from rest_framework.schemas.openapi import AutoSchema


class ReconPointsSchema(AutoSchema):
    """
    OpenAPI schema for reconstruct points method
    """

    def get_components(self, path, method):
        """
        override get_components
        """
        return super().get_components(path, method)

    def get_operation(self, path, method):
        """
        override get_operation
        """
        operation = super().get_operation(path, method)
        parameters = [
            {
                "name": "points",
                "in": "query",
                "description": """list of points long,lat comma separated coordinates of points to be reconstructed [Required or use "lats" and "lons" parameters]""",
                "schema": {"type": "number"},
            },
            {
                "name": "lats",
                "in": "query",
                "description": """list of latitudes of input points [Required or use "points" parameter]""",
                "schema": {"type": "number"},
            },
            {
                "name": "lons",
                "in": "query",
                "description": """list of latitudes of input points [Required or use "points" parameter]""",
                "schema": {"type": "number"},
            },
            {
                "name": "time",
                "in": "query",
                "description": "time for reconstruction [required]",
                "schema": {"type": "number"},
            },
            {
                "name": "times",
                "in": "query",
                "description": "multiple times(mutually exclusive with time) for reconstruction [required]",
                "schema": {"type": "list[float]"},
            },
            {
                "name": "anchor_plate_id",
                "in": "query",
                "description": "integer value for reconstruction anchor plate id [default=0]",
                "schema": {"type": "number"},
            },
            {
                "name": "model",
                "in": "query",
                "description": "name for reconstruction model [defaults to default model from web service settings]",
                "schema": {"type": "string"},
            },
            {
                "name": "pids",
                "in": "query",
                "description": "specify plate id for each point to improve performance",
                "schema": {"type": "list[int]"},
            },
            {
                "name": "pid",
                "in": "query",
                "description": "specify plate id to improve performance. all points use the same plate id. mutually exclusive with pids",
                "schema": {"type": "number"},
            },
            {
                "name": "return_null_points",
                "in": "query",
                "description": "use null to indicate invalid coordinates. otherwise, use [999.99, 999.99]",
                "schema": {"type": "boolean"},
            },
            {
                "name": "fc",
                "in": "query",
                "description": "flag to return geojson feature collection",
                "schema": {"type": "boolean"},
            },
            {
                "name": "reverse",
                "in": "query",
                "description": "reverse reconstruct paleo-coordinates to present-day coordinates",
                "schema": {"type": "boolean"},
            },
            {
                "name": "ignore_valid_time",
                "in": "query",
                "description": "if this flag presents, the reconstruction will ignore the valid time constraint",
                "schema": {"type": "boolean"},
            },
        ]
        responses = {
            "200": {
                "description": "reconstructed coordinates in json or geojson format",
                "content": {"application/json": {}},
            }
        }
        my_operation = {
            "parameters": parameters,
            "responses": responses,
        }
        if method.lower() == "get":
            my_operation["description"] = (
                """HTTP GET request to reconstruct points. For details and examples, go to https://gwsdoc.gplates.org/reconstruction/reconstruct-points"""
            )
            my_operation["summary"] = "GET method to reconstruct points"
        elif method.lower() == "post":
            my_operation["description"] = (
                """HTTP POST request to reconstruct points. For details and examples, go to https://gwsdoc.gplates.org/reconstruction/reconstruct-points"""
            )
            my_operation["summary"] = "POST method to reconstruct points"

        else:
            my_operation = {"summary": "Not implemented yet!"}

        operation.update(my_operation)
        return operation
