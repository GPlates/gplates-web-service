import io
import json
import math

import lib.rotation as rotation
import matplotlib.pyplot as plt
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, schema
from rest_framework.schemas.openapi import AutoSchema

from .icosahedron import get_mesh


def find_axis_and_angle(request):
    """
    http://localhost:18000/earth/find_axis_and_angle/?point_a=120,45&point_b=20,-45
    """
    point_a_str = request.GET.get("point_a", None)
    point_b_str = request.GET.get("point_b", None)
    if not point_a_str or not point_b_str:
        return HttpResponseBadRequest("Two points are required in the request!")
    try:
        point_a = point_a_str.split(",")
        point_b = point_b_str.split(",")

        lon_a = float(point_a[0])
        lat_a = float(point_a[1])
        lon_b = float(point_b[0])
        lat_b = float(point_b[1])
    except:
        return HttpResponseBadRequest("Invalid points!")

    axis, angle = rotation.find_axis_and_angle(
        (math.radians(lat_a), math.radians(lon_a)),
        (math.radians(lat_b), math.radians(lon_b)),
    )

    ret = {
        "axis": (math.degrees(axis[1]), math.degrees(axis[0])),
        "angle": math.degrees(angle),
    }

    response = HttpResponse(json.dumps(ret), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


def interp_two_locations(request):
    """
    http://localhost:18000/earth/interp_two_locations/?point_a=120,45&point_b=20,-45&num=10
    """
    point_a_str = request.GET.get("point_a", None)
    point_b_str = request.GET.get("point_b", None)
    num_str = request.GET.get("num", 10)
    if not point_a_str or not point_b_str:
        return HttpResponseBadRequest("Two points are required in the request!")
    try:
        point_a = point_a_str.split(",")
        point_b = point_b_str.split(",")

        lon_a = float(point_a[0])
        lat_a = float(point_a[1])
        lon_b = float(point_b[0])
        lat_b = float(point_b[1])

        num = int(num_str)
    except:
        return HttpResponseBadRequest("Invalid points!")

    points_r = rotation.interp_two_points(
        (math.radians(lat_a), math.radians(lon_a)),
        (math.radians(lat_b), math.radians(lon_b)),
        num,
    )

    points_d = [
        [round(math.degrees(p[1]), 4), round(math.degrees(p[0]), 4)] for p in points_r
    ]

    ret = {"locations": points_d}

    response = HttpResponse(json.dumps(ret), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


def distance(request):
    """
    http://localhost:18000/earth/distance/?point_a=120,45&point_b=20,-45
    calculate the greate arch length between two locations
    """
    point_a_str = request.GET.get("point_a", None)
    point_b_str = request.GET.get("point_b", None)

    if not point_a_str or not point_b_str:
        return HttpResponseBadRequest("Two points are required in the request!")
    try:
        point_a = point_a_str.split(",")
        point_b = point_b_str.split(",")

        lon_a = float(point_a[0])
        lat_a = float(point_a[1])
        lon_b = float(point_b[0])
        lat_b = float(point_b[1])

    except:
        return HttpResponseBadRequest("Invalid points!")

    distance = rotation.distance(
        (math.radians(lat_a), math.radians(lon_a)),
        (math.radians(lat_b), math.radians(lon_b)),
    )

    ret = {"distance": distance}

    response = HttpResponse(json.dumps(ret), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response


class GlobeMeshSchema(AutoSchema):
    """
    OpenAPI schema for get_globe_mesh() method
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
                "name": "level",
                "in": "query",
                "description": "how many time to bisect the icosahedron. max level 7, default level 3",
                "schema": {"type": "number"},
            },
            {
                "name": "fmt",
                "in": "query",
                "description": "return format. either json or png.",
                "schema": {"type": "string"},
            },
        ]
        responses = {
            "200": {
                "description": "return globe mesh either in json format or png image",
                "content": {"application/json": {}, "image/png": {}},
            }
        }
        my_operation = {
            "parameters": parameters,
            "responses": responses,
        }
        if method.lower() == "get":
            my_operation[
                "description"
            ] = "Get globe mesh created by bisecting icosahedron"
            my_operation[
                "summary"
            ] = "GET method to return globe mesh created by bisecting icosahedron"
        else:
            my_operation = {"summary": "Not implemented yet!"}

        operation.update(my_operation)
        return operation


@api_view(["GET"])
@schema(GlobeMeshSchema())
def get_globe_mesh(request):
    """
    return a mesh created by using icosahedron
    http://localhost:18000/earth/get_globe_mesh/?&level=2&fmt=png
    """
    level_str = request.GET.get("level", 3)
    format = request.GET.get("fmt", "json")
    try:
        level = int(level_str)
    except:
        level = 3
        print(f"invalid level parameter({level_str}), must be integer, use 3.")

    if level > 7:
        return HttpResponseBadRequest(
            "the level is not allowed to exceed 7 due to server constrain"
        )

    vertices, faces = get_mesh(level)

    ret = {"vertices": vertices.tolist(), "faces": faces.tolist()}

    # return a 3d png image of the globe mesh
    if format == "png":
        fig = plt.figure(figsize=(12, 12), dpi=300)
        ax = plt.axes(projection="3d")

        ax.plot_trisurf(
            vertices[:, 0],
            vertices[:, 1],
            vertices[:, 2],
            triangles=faces,
            cmap="jet",
            linewidths=1,
        )
        ax.view_init(elev=-160.0, azim=45)
        ax.set_box_aspect((1, 1, 0.9))

        imgdata = io.BytesIO()
        fig.savefig(
            imgdata,
            format="png",
            bbox_inches="tight",
            dpi=96,
            transparent=True,
            pad_inches=0,
        )

        imgdata.seek(0)  # rewind the data
        plt.clf()

        response = HttpResponse(imgdata.getvalue(), content_type="image/png")

    else:
        response = HttpResponse(json.dumps(ret), content_type="application/json")

    response["Access-Control-Allow-Origin"] = "*"
    return response
