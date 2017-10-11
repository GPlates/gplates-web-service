def write_json_reconstructed_point_features(reconstructed_points,attributes=None):
# create a json object from a reconstructed point feature - optionally with attributes
# assumed to be in a 'shapefile_attribute' field
# TODO implement gpgim attributes
# TODO implement types for attributes (string, float, etc)


    ret='{"type":"FeatureCollection","features":['
    for reconstructed_point in reconstructed_points:
        coords = [reconstructed_point.get_reconstructed_geometry().to_lat_lon()[1],
                  reconstructed_point.get_reconstructed_geometry().to_lat_lon()[0]]
        ret+='{"type":"Feature","geometry":'
        ret+='{'+'"type":"Point","coordinates":[{0:5.8f},{1:5.8f}]'.format(coords[0],coords[1])+'},'
        if attributes is not None:
            ret+='"properties":{'
            for attribute in attributes:
                attribute_string = '"%s":["%s"],' % (attribute[0],reconstructed_point.get_feature().get_shapefile_attribute(attribute[0]))
                ret+=attribute_string
            ret=ret[0:-1]
            ret+='}},'
        else:
            ret=ret[0:-1]
            ret+='},'

    ret=ret[0:-1]
    ret+=']}'

    return ret