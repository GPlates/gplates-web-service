import glob
import zipfile


#
#
#
def write_json_reconstructed_point_features(reconstructed_points, attributes=None):
    # create a json object from a reconstructed point feature - optionally with attributes
    # assumed to be in a 'shapefile_attribute' field
    # TODO implement gpgim attributes
    # TODO implement types for attributes (string, float, etc)

    ret = '{"type":"FeatureCollection","features":['
    for reconstructed_point in reconstructed_points:
        coords = [
            reconstructed_point.get_reconstructed_geometry().to_lat_lon()[1],
            reconstructed_point.get_reconstructed_geometry().to_lat_lon()[0],
        ]
        ret += '{"type":"Feature","geometry":'
        ret += (
            "{"
            + '"type":"Point","coordinates":[{0:5.8f},{1:5.8f}]'.format(
                coords[0], coords[1]
            )
            + "},"
        )
        if attributes is not None:
            ret += '"properties":{'
            for attribute in attributes:
                attribute_string = '"%s":["%s"],' % (
                    attribute[0],
                    reconstructed_point.get_feature().get_shapefile_attribute(
                        attribute[0]
                    ),
                )
                ret += attribute_string
            ret = ret[0:-1]
            ret += "}},"
        else:
            ret = ret[0:-1]
            ret += "},"

    ret = ret[0:-1]
    ret += "]}"

    return ret

    # save the files into the temporary dir


#
#
#
def save_upload_files(request, tmp_dir):
    for fs in request.FILES.lists():
        for f in fs[1]:
            # print((f.name))
            with open(f"{tmp_dir}/{f.name}", "wb+") as fp:
                for chunk in f.chunks():
                    fp.write(chunk)


# find and unzip all zip files
def find_and_unzip_all_zip_files(tmp_dir):
    zip_files = glob.glob(f"{tmp_dir}/**/*.zip", recursive=True)
    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(tmp_dir)


# Raised when pygplates failed to produce output files
class NoOutputFileError(Exception):
    error_msg = (
        f"Error: No output files have been created! "
        + "You might need to add 'assign_plate_id=1' to your http request."
    )

    def print_error(self):
        print(self.error_msg)
