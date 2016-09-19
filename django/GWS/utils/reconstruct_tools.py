
def reconstruct_to_birth_time(features,rotation_model):

    reconstructed_features = []

    for feature in features:

        # NB valid_time is a tuple, we take the first value since this is the 'birth' time of the LIP
        BirthTime = feature.get_valid_time()[0]
        PlateID = feature.get_reconstruction_plate_id()

        # Get rotation for data point and reconstruct to Birth Time
        feature_rotation = rotation_model.get_rotation(BirthTime, PlateID, anchor_plate_id=0)

        reconstructed_geometry = feature_rotation * feature.get_geometry()

        new_feature = feature
        new_feature.set_geometry(reconstructed_geometry)
        reconstructed_features.append(new_feature)

    return reconstructed_features
