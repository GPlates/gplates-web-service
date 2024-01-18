#!/usr/bin/env python3
import os

import pygplates
import requests


def reduce_resolution(lat_lon_list, min_distance=20):
    """merge points according to the min_distance"""
    assert len(lat_lon_list) > 2

    current_point = lat_lon_list[0]
    points = [current_point]

    for lat_lon in lat_lon_list:
        distance = pygplates.GeometryOnSphere.distance(
            pygplates.PointOnSphere(lat_lon), pygplates.PointOnSphere(current_point)
        )
        if distance > 20 / pygplates.Earth.mean_radius_in_kms:
            points.append(current_point)
            current_point = lat_lon

    return points


def downsample_polygons(feature_collection, min_area=30000, min_distance=20):
    """downsample the polygons
    remove all smaller polygons with area less than min_area
    merge points of polygons according to the min_distance
    """
    polygons = []
    valid_times = []
    pids = []
    for f in feature_collection:
        geoms = f.get_geometries()
        for g in geoms:
            if isinstance(g, pygplates.PolygonOnSphere):
                # print(geom.get_area())
                points = g.get_exterior_ring_points()
                points = reduce_resolution(points, min_distance)
                if len(points) > 2:
                    geom = pygplates.PolygonOnSphere(points)
                    if geom.get_area() > min_area / (
                        pygplates.Earth.mean_radius_in_kms**2
                    ):
                        b_time, e_time = f.get_valid_time()
                        valid_times.append((b_time, e_time))
                        pids.append(f.get_reconstruction_plate_id())
                        # print(geom.get_orientation())
                        if (
                            geom.get_orientation()
                            != pygplates.PolygonOnSphere.Orientation.clockwise
                        ):
                            polygons.append(
                                pygplates.PolygonOnSphere(geom.to_lat_lon_list()[::-1])
                            )
                        else:
                            polygons.append(geom)

    # print(len(polygons))

    fc_o = pygplates.FeatureCollection()
    for p, time, pid in zip(polygons, valid_times, pids):
        f = pygplates.Feature()
        f.set_geometry(p)
        f.set_valid_time(time[0], time[1])
        f.set_reconstruction_plate_id(pid)
        fc_o.add(f)
    return fc_o


if __name__ == "__main__":
    FILENAME = "coastlines.gpmlz"

    if not os.path.isfile(FILENAME):
        r = requests.get(
            "https://repo.gplates.org/webdav/mchin/data/Global_EarthByte_GPlates_PresentDay_Coastlines.gpmlz"
        )
        open(FILENAME, "wb").write(r.content)

    fc_o = downsample_polygons(pygplates.FeatureCollection(FILENAME), 30000, 20)
    fc_o.write("coastlines_downsampled.gpmlz")
