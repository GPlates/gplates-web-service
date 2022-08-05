import json

import pygplates


#
# load geojson and return pygplates feature collection
#
def load_geojson(geojson_str, keep_properties=True):
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


#
# convert pygplates feature collection to geojson
#
def save_reconstructed_geometries_geojson(
    reconstructed_geometries, keep_properties=True
):
    data = {"type": "FeatureCollection"}
    data["features"] = []
    for g in reconstructed_geometries:
        geom = g.get_reconstructed_geometry()
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
            feature["geometry"]["type"] = "LineString"
            feature["geometry"]["coordinates"] = [
                [lon, lat] for lat, lon in geom.to_lat_lon_list()
            ]
        elif isinstance(geom, pygplates.PolygonOnSphere):
            feature["geometry"]["type"] = "Polygon"
            feature["geometry"]["coordinates"] = [
                [[lon, lat] for lat, lon in geom.to_lat_lon_list()]
            ]
        else:
            raise UnsupportedGeometryType()

        feature["properties"] = {}
        if keep_properties:
            for pk in g.get_feature().get_shapefile_attributes():
                feature["properties"][pk] = g.get_feature().get_shapefile_attribute(pk)
        # print feature["properties"]
        data["features"].append(feature)
    return data


class UnsupportedGeometryType(Exception):
    pass
