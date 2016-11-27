#
# Functions for wrapping geometries to dateline before returning request geojson
#

import pygplates


def wrap_polylines(polylines,lon0=0,tesselate_degrees=1):
    
    wrapper = pygplates.DateLineWrapper(lon0)
    
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for polyline in polylines:

        split_geometry = wrapper.wrap(polyline.get_geometry(),tesselate_degrees)
        for geometry in split_geometry:
            feature = {"type": "Feature"}
            feature["geometry"] = {}
            feature["geometry"]["type"] = "MultiLineString"
            point_list = []
            for point in geometry.get_points():
                point_list.append((point.to_lat_lon()[1],point.to_lat_lon()[0]))
            feature["geometry"]["coordinates"] = [point_list]
            data["features"].append(feature)
 
    return data

def wrap_polygons(polygons,lon0=0,tesselate_degrees=1):
    
    wrapper = pygplates.DateLineWrapper(lon0)
    
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for polygon in polygons:
        split_geometry = wrapper.wrap(polygon.get_geometry(),tesselate_degrees)
        for geometry in split_geometry:
            feature = {"type": "Feature"}
            feature["geometry"] = {}
            feature["geometry"]["type"] = "Polygon"
            point_list = []
            for point in geometry.get_exterior_points():
                point_list.append((point.to_lat_lon()[1],point.to_lat_lon()[0]))
            feature["geometry"]["coordinates"] = [point_list]
            data["features"].append(feature)
    
    return data

def wrap_reconstructed_polygons(reconstructed_polygons,lon0=0,tesselate_degrees=1):
    
    wrapper = pygplates.DateLineWrapper(lon0)
    
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for reconstructed_polygon in reconstructed_polygons:
        split_geometry = wrapper.wrap(reconstructed_polygon.get_reconstructed_geometry(),tesselate_degrees)
        for geometry in split_geometry:
            feature = {"type": "Feature"}
            feature["geometry"] = {}
            feature["geometry"]["type"] = "Polygon"
            point_list = []
            for point in geometry.get_exterior_points():
                point_list.append((point.to_lat_lon()[1],point.to_lat_lon()[0]))
            feature["geometry"]["coordinates"] = [point_list]
            data["features"].append(feature)
    
    return data

def wrap_plate_boundaries(shared_boundary_sections,lon0=0,tesselate_degrees=1):
    
    wrapper = pygplates.DateLineWrapper(lon0)
    
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for shared_boundary_section in shared_boundary_sections:
        for shared_sub_segment in shared_boundary_section.get_shared_sub_segments():

            split_geometry = wrapper.wrap(shared_sub_segment.get_geometry(),tesselate_degrees)
            for geometry in split_geometry:
                feature = {"type": "Feature"}
                feature["geometry"] = {}
                feature["geometry"]["type"] = "MultiLineString"
                point_list = []
                for point in geometry.get_points():
                    point_list.append((point.to_lat_lon()[1],point.to_lat_lon()[0]))
                feature["geometry"]["coordinates"] = [point_list]
                feature["feature_type"] = str(shared_sub_segment.get_feature().get_feature_type())
                feature["Length"] = float(shared_sub_segment.get_geometry().get_arc_length())
                data["features"].append(feature)
    
    return data
