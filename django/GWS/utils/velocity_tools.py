import pygplates
from create_gpml import create_gpml_healpix_mesh

def get_velocities(rotation_model,topology_features,time,velocity_domain_features=None,delta_time=1):

    if velocity_domain_features is None:
        velocity_domain_features = create_gpml_healpix_mesh(32,feature_type='MeshNode')

    # All domain points and associated (magnitude, azimuth, inclination) velocities for the current time.
    all_domain_points = []
    all_velocities = []

    # Partition our velocity domain features into our topological plate polygons at the current 'time'.
    plate_partitioner = pygplates.PlatePartitioner(topology_features, rotation_model, time)

    for velocity_domain_feature in velocity_domain_features:

        # A velocity domain feature usually has a single geometry but we'll assume it can be any number.
        # Iterate over them all.
        for velocity_domain_geometry in velocity_domain_feature.get_geometries():

            for velocity_domain_point in velocity_domain_geometry.get_points():

                all_domain_points.append(velocity_domain_point)

                partitioning_plate = plate_partitioner.partition_point(velocity_domain_point)
                if partitioning_plate:

                    # We need the newly assigned plate ID to get the equivalent stage rotation of that tectonic plate.
                    partitioning_plate_id = partitioning_plate.get_feature().get_reconstruction_plate_id()

                    # Get the stage rotation of partitioning plate from 'time + delta_time' to 'time'.
                    equivalent_stage_rotation = rotation_model.get_rotation(time, partitioning_plate_id, time + delta_time)

                    # Calculate velocity at the velocity domain point.
                    # This is from 'time + delta_time' to 'time' on the partitioning plate.
                    velocity_vectors = pygplates.calculate_velocities(
                        [velocity_domain_point],
                        equivalent_stage_rotation,
                        delta_time)

                    # Convert global 3D velocity vectors to local (magnitude, azimuth, inclination) tuples (one tuple per point).
                    velocities = pygplates.LocalCartesian.convert_from_geocentric_to_magnitude_azimuth_inclination(
                            [velocity_domain_point],
                            velocity_vectors)
                    all_velocities.append(velocities[0])

                else:
                    all_velocities.append((0,0,0))

    pt_vel_mag=[]
    pt_vel_az=[]
    for velocity_vector in all_velocities:
        pt_vel_mag.append(velocity_vector[0])
        pt_vel_az.append(velocity_vector[1])

    pt_lon = []
    pt_lat = []
    for pt in all_domain_points:
        pt_lon.append(pt.to_lat_lon()[1])
        pt_lat.append(pt.to_lat_lon()[0])

    return pt_lat,pt_lon,pt_vel_mag,pt_vel_az
