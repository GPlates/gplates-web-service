import json

import pygplates


#
# load geojson and return pygplates feature collection
#
def load_geojson(geojson_str, keep_properties=True):
    features = []
    try:
        fc = json.loads(geojson_str)  # load the input feature collection
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

            features.append(feature)
    except Exception as e:
        raise e

    return pygplates.FeatureCollection(features)
