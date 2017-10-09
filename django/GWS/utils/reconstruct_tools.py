import pygplates

def reconstruct_to_birth_time(features,rotation_model,ReconstructTime='BeginTime'):

    reconstructed_features = []

    for feature in features:

        # NB valid_time is a tuple, we take the first value since this is the 'birth' time of the LIP
        if ReconstructTime is 'MidTime':
            time = (feature.get_valid_time()[0]+feature.get_valid_time()[1])/2.
        else:
            time = feature.get_valid_time()[0]
        PlateID = feature.get_reconstruction_plate_id()

        # Get rotation for data point and reconstruct to Birth Time
        feature_rotation = rotation_model.get_rotation(time, PlateID, anchor_plate_id=0)

        reconstructed_geometry = feature_rotation * feature.get_geometry()

        new_feature = feature
        new_feature.set_geometry(reconstructed_geometry)
        reconstructed_features.append(new_feature)

    return reconstructed_features


def reconstruct_vgps(vgp_features,rotation_model,anchor_plate_id=0):

    reconstructed_vgps = []

    for vgp in vgp_features:
        
        time = vgp.get(pygplates.PropertyName.gpml_average_age).get_value().get_double()
        PlateID = vgp.get_reconstruction_plate_id()
        geometry = vgp.get(pygplates.PropertyName.gpml_pole_position).get_value().get_geometry()

        #print time,PlateID,geometry.to_lat_lon()
        
        # Get rotation for data point and reconstruct to Birth Time
        feature_rotation = rotation_model.get_rotation(time, PlateID, anchor_plate_id)

        reconstructed_geometry = feature_rotation * geometry

        #print PlateID,reconstructed_geometry.to_lat_lon()
        
        new_feature = pygplates.Feature()
        new_feature.set_geometry(reconstructed_geometry)
        new_feature.set_reconstruction_plate_id(PlateID)
        new_feature.set_valid_time(time,-999)
        new_feature.set(pygplates.PropertyName.gpml_average_age,pygplates.XsDouble(time))
        new_feature.set(pygplates.PropertyName.gpml_pole_a95,
                        vgp.get(pygplates.PropertyName.gpml_pole_a95).get_value())
        reconstructed_vgps.append(new_feature)

    return reconstructed_vgps


