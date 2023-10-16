import json

import pygplates


def load_geojson(geojson_str, keep_properties=True):
    """load geojson and return pygplates feature collection"""
    features = []
    try:
        fc = json.loads(geojson_str)  # load the input feature collection
        idx = 0
        for f in fc["features"]:
            geom = f["geometry"]
            feature = pygplates.Feature()
            if geom["type"] == "Point":
                feature.set_geometry(
                    pygplates.PointOnSphere(
                        float(geom["coordinates"][1]), float(geom["coordinates"][0])
                    )
                )
            if geom["type"] == "LineString":
                feature.set_geometry(
                    pygplates.PolylineOnSphere(
                        [(point[1], point[0]) for point in geom["coordinates"]]
                    )
                )
            if geom["type"] == "Polygon":
                feature.set_geometry(
                    pygplates.PolygonOnSphere(
                        [(point[1], point[0]) for point in geom["coordinates"][0]]
                    )
                )
            if geom["type"] == "MultiPoint":
                feature.set_geometry(
                    pygplates.MultiPointOnSphere(
                        [(point[1], point[0]) for point in geom["coordinates"]]
                    )
                )

            if keep_properties and "properties" in f:
                for pk in f["properties"]:
                    p = f["properties"][pk]
                    if isinstance(p, str):
                        p = str(p)
                    feature.set_shapefile_attribute(str(pk), p)

            feature.set_name(str(idx))
            idx += 1

            features.append(feature)
    except Exception as e:
        raise e

    return pygplates.FeatureCollection(features)


def save_reconstructed_geometries_geojson(
    reconstructed_geometries, keep_properties=True
):
    """convert pygplates.ReconstructedFeatureGeometry objects to geojson feature collection"""

    geoms = [g.get_reconstructed_geometry() for g in reconstructed_geometries]
    list_of_properties = [
        g.get_feature().get_shapefile_attributes() for g in reconstructed_geometries
    ]

    data = {"type": "FeatureCollection"}
    data["features"] = dump_geojson(geoms, list_of_properties=list_of_properties)
    return data


def dump_geojson(
    geometries: list[pygplates.GeometryOnSphere],
    list_of_properties: list[dict] = None,
    date_line_wrapper=pygplates.DateLineWrapper(0),
    tesselate_degrees=1,
):
    """convert a list of pygplates.GeometryOnSphere to a list of geojson features"""
    if list_of_properties:
        assert len(geometries) == len(list_of_properties)
    else:
        list_of_properties = [{}] * len(geometries)

    features = []
    for geom, properties in zip(geometries, list_of_properties):
        if not geom:
            continue
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        if isinstance(geom, pygplates.PointOnSphere):
            feature["geometry"]["type"] = "Point"
            p = geom.to_lat_lon_list()[0]
            feature["geometry"]["coordinates"] = [p[1], p[0]]
        elif isinstance(geom, pygplates.MultiPointOnSphere):
            feature["geometry"]["type"] = "MultiPoint"
            feature["geometry"]["coordinates"] = [
                [lon, lat] for lat, lon in geom.to_lat_lon_list()
            ]
        elif isinstance(geom, pygplates.PolylineOnSphere):
            if date_line_wrapper:
                geometries = date_line_wrapper.wrap(geom, tesselate_degrees)
            else:
                geometries = [geom]

            if len(geometries) > 1:
                feature["geometry"]["type"] = "MultiLineString"
                feature["geometry"]["coordinates"] = []
                for g in geometries:
                    feature["geometry"]["coordinates"].append(
                        [
                            [point.to_lat_lon()[1], point.to_lat_lon()[0]]
                            for point in g.get_points()
                        ]
                    )
            else:
                feature["geometry"]["type"] = "LineString"
                feature["geometry"]["coordinates"] = [
                    [lon, lat] for lat, lon in geom.to_lat_lon_list()
                ]
        elif isinstance(geom, pygplates.PolygonOnSphere):
            if date_line_wrapper:
                geometries = date_line_wrapper.wrap(geom, tesselate_degrees)
            else:
                geometries = [geom]

            if len(geometries) > 1:
                feature["geometry"]["type"] = "MultiPolygon"
                feature["geometry"]["coordinates"] = []
                for g in geometries:
                    feature["geometry"]["coordinates"].append(
                        [
                            [point.to_lat_lon()[1], point.to_lat_lon()[0]]
                            for point in g.get_exterior_points()
                        ]
                    )
            else:
                feature["geometry"]["type"] = "Polygon"
                feature["geometry"]["coordinates"] = [
                    [[lon, lat] for lat, lon in geom.to_lat_lon_list()]
                ]
        else:
            print("geometry: " + geom)
            raise UnsupportedGeometryType()

        feature["properties"] = properties

        features.append(feature)
    return features


class UnsupportedGeometryType(Exception):
    pass
