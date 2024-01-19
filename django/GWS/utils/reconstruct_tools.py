import logging
import math

import pygplates
from utils.plate_model_utils import (
    UnrecognizedModel,
    get_rotation_model,
    get_static_polygons,
)

logger = logging.getLogger("default")


def reconstruct_to_birth_time(features, rotation_model, ReconstructTime="BeginTime"):
    """reconstruct features to its birth time"""
    reconstructed_features = []

    for feature in features:
        # NB valid_time is a tuple, we take the first value since this is the 'birth' time of the LIP
        if ReconstructTime == "MidTime":
            time = (feature.get_valid_time()[0] + feature.get_valid_time()[1]) / 2.0
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


def reconstruct_vgps(vgp_features, rotation_model, anchor_plate_id=0):
    """reconstruct VGPs"""
    reconstructed_vgps = []

    for vgp in vgp_features:
        time = vgp.get(pygplates.PropertyName.gpml_average_age).get_value().get_double()
        PlateID = vgp.get_reconstruction_plate_id()
        geometry = (
            vgp.get(pygplates.PropertyName.gpml_pole_position)
            .get_value()
            .get_geometry()
        )

        # print time,PlateID,geometry.to_lat_lon()

        # Get rotation for data point and reconstruct to Birth Time
        feature_rotation = rotation_model.get_rotation(time, PlateID, anchor_plate_id)

        reconstructed_geometry = feature_rotation * geometry

        # print PlateID,reconstructed_geometry.to_lat_lon()

        new_feature = pygplates.Feature()
        new_feature.set_geometry(reconstructed_geometry)
        new_feature.set_reconstruction_plate_id(PlateID)
        new_feature.set_valid_time(time, -999)
        new_feature.set(
            pygplates.PropertyName.gpml_average_age, pygplates.XsDouble(time)
        )
        new_feature.set(
            pygplates.PropertyName.gpml_pole_a95,
            vgp.get(pygplates.PropertyName.gpml_pole_a95).get_value(),
        )
        reconstructed_vgps.append(new_feature)

    return reconstructed_vgps


def assign_plate_ids(
    geoms,
    model,
    time=0.0,
    method=pygplates.PartitionMethod.most_overlapping_plate,
):
    """assign plate ids for geometries

    :param time: the paleo-age at which to assign plate IDs
    """
    pid_and_time = []
    try:
        rotation_model = get_rotation_model(model)

        features = []
        index = 0
        for geom in geoms:
            feature = pygplates.Feature()
            feature.set_geometry(geom)
            feature.set_name(str(index))
            features.append(feature)
            index += 1

        # assign plate-ids to geometries using static polygons
        assigned_features = pygplates.partition_into_plates(
            get_static_polygons(model),
            rotation_model,
            features,
            properties_to_copy=[
                pygplates.PartitionProperty.reconstruction_plate_id,
                pygplates.PartitionProperty.valid_time_period,
            ],
            reconstruction_time=time,
            partition_method=method,
        )

        assert len(features) == len(assigned_features)

        pid_and_time_dict = {}
        for f in assigned_features:
            begin_time, end_time = f.get_valid_time(default=(None, None))

            if math.isinf(begin_time):
                begin_time = None
            if math.isinf(end_time):
                end_time = None
            pid_and_time_dict[f.get_name()] = (
                f.get_reconstruction_plate_id(),
                begin_time,
                end_time,
            )

        for i in range(0, len(assigned_features)):
            # make sure the order of features is correct
            pid_and_time.append(pid_and_time_dict[str(i)])

    except UnrecognizedModel as e:
        logger.error(
            f"""Unrecognized Rotation Model: {model}.
        Use <a href="https://gws.gplates.org/info/model_names">https://gws.gplates.org/info/model_names</a>
        to find all available models."""
        )
    except pygplates.InvalidLatLonError as e:
        logger.error(f"Invalid longitude or latitude ({e}).")
    except ValueError as e:
        logger.error(f"Invalid value ({e}).")
    finally:
        return pid_and_time
