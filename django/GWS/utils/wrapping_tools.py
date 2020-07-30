#
# Functions for wrapping geometries to dateline before returning request geojson
#

import pygplates


def wrap_polylines(polylines,lon0=0,tesselate_degrees=1):
    
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for polyline in polylines:

        if lon0 is not None:
            wrapper = pygplates.DateLineWrapper(central_meridian)
            geometries = wrapper.wrap(polyline.get_geometry(),tesselate_degrees)
        else:
            geometries = polyline.get_geometries()

        for geometry in geometries:
            feature = {"type": "Feature"}
            feature["geometry"] = {}
            feature["geometry"]["type"] = "MultiLineString"
            point_list = []
            for point in geometry.get_points():
                point_list.append((point.to_lat_lon()[1],point.to_lat_lon()[0]))
            feature["geometry"]["coordinates"] = [point_list]
            data["features"].append(feature)
 
    return data


def wrap_resolved_polygons(resolved_polygons,
                           wrap=False,
                           central_meridian=0,
                           avoid_map_boundary=False,
                           tesselate_degrees=2):
    
    polygons=[]
    if wrap:
        wrapped_polygons=[]
        date_line_wrapper = pygplates.DateLineWrapper(central_meridian)
        for p in resolved_polygons:
            wrapped_polygons += date_line_wrapper.wrap(p.get_geometry(),tesselate_degrees)
        for p in wrapped_polygons:
            lats=[i.get_latitude() for i in p.get_exterior_points()]
            lons=[i.get_longitude() for i in p.get_exterior_points()]
            if pygplates.PolygonOnSphere(list(zip(lats,lons))).get_orientation() == pygplates.PolygonOnSphere.Orientation.clockwise:
                polygons.append((lons,lats))
            else:
                polygons.append((lons[::-1],lats[::-1]))
    else:
        for p in resolved_polygons:
            lats, lons = list(zip( *p.get_geometry().to_lat_lon_list()))
            lats = list(lats)
            lons = list(lons)
            if pygplates.PolygonOnSphere(list(zip(lats,lons))).get_orientation() == pygplates.PolygonOnSphere.Orientation.clockwise:
                polygons.append((lons,lats))
            else:
                polygons.append((lons[::-1],lats[::-1]))

    data = {"type": "FeatureCollection"}
    data["features"] = []
    for p in polygons:
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        feature["geometry"]["type"] = "Polygon"

        #make sure the coordinates are valid.
        lats=p[1]
        lons=p[0]
        #print lats, lons
        #some map plotting program(such as leaflet) does not like points on the map boundary,
        #for example the longitude 180 and -180.
        #So, move the points slightly inwards.
        if avoid_map_boundary:
            for idx, x in enumerate(lons):
                if x<central_meridian-179.99:
                    lons[idx] = central_meridian-179.99
                elif x>central_meridian+179.99:
                    lons[idx] = central_meridian+179.99
            for idx, x in enumerate(lats):
                if x<-89.99:
                    lats[idx] = -89.99
                elif x>89.99:
                    lats[idx] = 89.99
        
        feature["geometry"]["coordinates"] = [list(zip(lons+lons[:1],lats+lats[:1]))]
        data["features"].append(feature)
    
    return data


def wrap_reconstructed_polygons(reconstructed_polygons,lon0=0,tesselate_degrees=1):
        
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for reconstructed_polygon in reconstructed_polygons:
        rev=False
        print(reconstructed_polygon.get_reconstructed_geometry().get_orientation())
        if reconstructed_polygon.get_reconstructed_geometry().get_orientation() == pygplates.PolygonOnSphere.Orientation.counter_clockwise:
            print('hello')
            rev = True

        if lon0 is not None:
            wrapper = pygplates.DateLineWrapper(lon0)
            geometries = wrapper.wrap(reconstructed_polygon.get_reconstructed_geometry(),tesselate_degrees)

            for geometry in geometries:
                feature = {"type": "Feature"}
                feature["geometry"] = {}
                feature["geometry"]["type"] = "Polygon"
                point_list = []
                for point in geometry.get_exterior_points():
                    point_list.append((point.to_lat_lon()[1],point.to_lat_lon()[0]))
                if rev:
                    point_list.reverse()
                feature["geometry"]["coordinates"] = [point_list]
                data["features"].append(feature)

        else:
            geometry = reconstructed_polygon.get_reconstructed_geometry()
            feature = {"type": "Feature"}
            feature["geometry"] = {}
            feature["geometry"]["type"] = "Polygon"
            point_list = []
            for point in geometry.get_points():
                point_list.append((point.to_lat_lon()[1],point.to_lat_lon()[0]))
            if rev:
                point_list.reverse()
            feature["geometry"]["coordinates"] = [point_list]
            data["features"].append(feature)
    
    return data

def wrap_plate_boundaries(shared_boundary_sections,lon0=0,tesselate_degrees=1):
        
    data = {"type": "FeatureCollection"}
    data["features"] = [] 
    for shared_boundary_section in shared_boundary_sections:
        for shared_sub_segment in shared_boundary_section.get_shared_sub_segments():

            if lon0 is not None:
                wrapper = pygplates.DateLineWrapper(lon0)
                geometries = wrapper.wrap(shared_sub_segment.get_geometry(),tesselate_degrees)
            else:
                geometries = shared_sub_segment.get_geometries()

            for geometry in geometries:
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


def process_reconstructed_polygons(reconstructed_polygons,
                                   wrap=False,
                                   central_meridian=0,
                                   avoid_map_boundary=False,
                                   tesselate_degrees=2):

    polygons=[]
    if wrap:
        wrapped_polygons=[]
        date_line_wrapper = pygplates.DateLineWrapper(central_meridian)
        for p in reconstructed_polygons:
            wrapped_polygons += date_line_wrapper.wrap(p.get_reconstructed_geometry(),tesselate_degrees)
        for p in wrapped_polygons:
            lats=[i.get_latitude() for i in p.get_exterior_points()]
            lons=[i.get_longitude() for i in p.get_exterior_points()]
            if pygplates.PolygonOnSphere(list(zip(lats,lons))).get_orientation() == pygplates.PolygonOnSphere.Orientation.clockwise:
                polygons.append((lons,lats))
            else:
                polygons.append((lons[::-1],lats[::-1]))
    else:
        for p in reconstructed_polygons:
            lats, lons = list(zip( *p.get_reconstructed_geometry().to_lat_lon_list()))
            lats = list(lats)
            lons = list(lons)
            if pygplates.PolygonOnSphere(list(zip(lats,lons))).get_orientation() == pygplates.PolygonOnSphere.Orientation.clockwise:
                polygons.append((lons,lats))
            else:
                polygons.append((lons[::-1],lats[::-1]))

    data = {"type": "FeatureCollection"}
    data["features"] = []
    for p in polygons:
        feature = {"type": "Feature"}
        feature["geometry"] = {}
        feature["geometry"]["type"] = "Polygon"

        #make sure the coordinates are valid.
        lats=p[1]
        lons=p[0]
        #print lats, lons
        #some map plotting program(such as leaflet) does not like points on the map boundary,
        #for example the longitude 180 and -180.
        #So, move the points slightly inwards.
        if avoid_map_boundary:
            for idx, x in enumerate(lons):
                if x<central_meridian-179.99:
                    lons[idx] = central_meridian-179.99
                elif x>central_meridian+179.99:
                    lons[idx] = central_meridian+179.99
            for idx, x in enumerate(lats):
                if x<-89.99:
                    lats[idx] = -89.99
                elif x>89.99:
                    lats[idx] = 89.99
        
        feature["geometry"]["coordinates"] = [list(zip(lons+lons[:1],lats+lats[:1]))]
        data["features"].append(feature)

    return data

