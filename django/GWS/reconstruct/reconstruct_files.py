#
# put your copyright, software license and legal information here.
#
import glob
import io
import os
import sys
import tempfile
import traceback
import zipfile
from pathlib import Path

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from geo.Geoserver import Geoserver
from utils.fileio import (
    save_upload_files,
    find_and_unzip_all_zip_files,
    NoOutputFileError,
)
from utils.model_utils import get_rotation_model, get_static_polygons, UnrecognizedModel


#
# reconstruct uploaded files
#
@csrf_exempt
def reconstruct(request):
    if not request.method == "POST":
        return HttpResponseBadRequest("ERROR: only post requests are accepted!")
    try:
        # print((request.FILES))
        if not len(list(request.FILES.items())):
            return HttpResponseBadRequest(
                "ERROR: No file has been received!"
                + " Your request must contain the files to be reconstructed. "
                + 'such as use the html input <input type="file" id="files" name="files" multiple>'
            )

        # create temporary dir to save intermediate files, remember to remove it after use
        with tempfile.TemporaryDirectory(prefix="gws-recon-files-tmp") as tmp_dir:
            # save the upload files into the temporary dir
            save_upload_files(request, tmp_dir)

            # get parameters from the http post request
            (
                time,
                model,
                assign_plate_id_flag,
                output_basename,
                save_plate_id_flag,
                geosrv_url,
                geosrv_username,
                geosrv_password,
                geosrv_workspace,
            ) = get_request_parameters(request)

            ignore_valid_time = True if "ignore_valid_time" in request.POST else False

            upload_result_to_geoserver_flag = (
                geosrv_url and geosrv_username and geosrv_password and geosrv_workspace
            )

            # find and unzip all zip files
            find_and_unzip_all_zip_files(tmp_dir)

            reconstructable_files = []
            reconstructable_files = glob.glob(f"{tmp_dir}/**/*.shp", recursive=True)
            reconstructable_files += glob.glob(f"{tmp_dir}/**/*.gpml", recursive=True)
            reconstructable_files += glob.glob(f"{tmp_dir}/**/*.gpmlz", recursive=True)
            # print(reconstructable_files)

            try:
                rotation_model = get_rotation_model(model)
            except UnrecognizedModel as e:
                return HttpResponseBadRequest(
                    f"""Unrecognized Rotation Model: {model}.<br> 
                    Use <a href="https://gws.gplates.org/info/model_names">https://gws.gplates.org/info/model_names</a> 
                    to find all available models."""
                )

            # create output folder
            output_path = f"{tmp_dir}/output/"
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # print(assign_plate_id_flag)
            if assign_plate_id_flag:  # assign plate id and then reconstruct
                feature_collection = pygplates.FeatureCollection()
                for f in reconstructable_files:
                    # print(f)
                    properties_to_copy = [
                        pygplates.PartitionProperty.reconstruction_plate_id
                    ]
                    if not ignore_valid_time:
                        properties_to_copy.append(
                            pygplates.PartitionProperty.valid_time_period
                        )

                    features = pygplates.partition_into_plates(
                        get_static_polygons(model),
                        rotation_model,
                        f,
                        partition_method=pygplates.PartitionMethod.most_overlapping_plate,
                        properties_to_copy=properties_to_copy,
                    )
                    if save_plate_id_flag:
                        pygplates.FeatureCollection(features).write(
                            f"{output_path}/{os.path.basename(f)}-with-plate-ids.shp"
                        )
                    feature_collection.add(features)

                pygplates.reconstruct(
                    feature_collection,
                    rotation_model,
                    f"{output_path}/{output_basename}.shp",
                    float(time),
                )
            else:  # when assign_plate_id_flag = False, do not assign plate id, just reconstruct straightaway
                pygplates.reconstruct(
                    reconstructable_files,
                    rotation_model,
                    f"{output_path}/{output_basename}.shp",
                    float(time),
                )

            if upload_result_to_geoserver_flag:
                upload_result_to_geoserver(
                    geosrv_url,
                    geosrv_username,
                    geosrv_password,
                    geosrv_workspace,
                    output_path,
                    output_basename,
                )
                return HttpResponse(
                    f"{geosrv_url}/{geosrv_workspace}/{output_basename}"
                )

            # print(os.listdir(output_path))
            s = io.BytesIO()
            with zipfile.ZipFile(s, "w") as zf:
                for r, _, files in os.walk(output_path):
                    if not files:
                        raise NoOutputFileError

                    for f in files:
                        # print(os.path.join(r, f))
                        zf.write(
                            str(os.path.join(r, f)), f
                        )  # the second argument is the file path inside the zip archive.

            response = HttpResponse(
                s.getvalue(), content_type="application/x-zip-compressed"
            )
            response[
                "Content-Disposition"
            ] = f"attachment; filename={output_basename}.zip"

            return response
    except NoOutputFileError as e:
        e.print_error()
        return HttpResponseBadRequest(NoOutputFileError.error_msg)
    except:
        traceback.print_stack()
        traceback.print_exc(file=sys.stdout)
        err = traceback.format_exc()
        return HttpResponseServerError(err)


# unused function
# remove all files from a folder
def clear_folder(path):
    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


# get parameters from the http post request
def get_request_parameters(request):
    time = request.POST.get("time", 0)
    model = request.POST.get("model", settings.MODEL_DEFAULT)
    out_fn = request.POST.get("basename", "reconstructed_files")
    assign_plate_id_flag = request.POST.get("assign_plate_id", True)
    save_plate_id_flag = request.POST.get("save_plate_id", False)
    geosrv_url = request.POST.get("geosrv_url", None)
    geosrv_username = request.POST.get("geosrv_username", None)
    geosrv_password = request.POST.get("geosrv_password", None)
    geosrv_workspace = request.POST.get("geosrv_workspace", None)

    try:
        if 0 == int(assign_plate_id_flag):
            assign_plate_id_flag = False
        else:
            assign_plate_id_flag = True
        if 1 == int(save_plate_id_flag):
            save_plate_id_flag = True
        else:
            save_plate_id_flag = False
    except:
        pass  # do nothing, use the default value
    if save_plate_id_flag:
        assign_plate_id_flag = True  # save_plate_id_flag overrides assign_plate_id_flag
    # print(save_plate_id_flag, "save_plate_id_flag")
    output_basename = f"{out_fn}-{time}Ma"
    return (
        time,
        model,
        assign_plate_id_flag,
        output_basename,
        save_plate_id_flag,
        geosrv_url,
        geosrv_username,
        geosrv_password,
        geosrv_workspace,
    )


def upload_result_to_geoserver(
    geosrv_url,
    geosrv_username,
    geosrv_password,
    geosrv_workspace,
    output_path,
    output_basename,
):
    shp_files = glob.glob(f"{output_path}/{output_basename}*")

    if 0 == len(shp_files):
        raise NoOutputFileError()

    with zipfile.ZipFile(f"{output_path}/{output_basename}.zip", "w") as zf:
        for fn in shp_files:
            # print(fn)
            # the second argument is the file path inside the zip archive.
            zf.write(fn, os.path.basename(fn))

    geo = Geoserver(geosrv_url, geosrv_username, geosrv_password)

    r = geo.create_workspace(workspace=geosrv_workspace)
    # print(r)
    r = geo.create_shp_datastore(
        # make sure you have this zip file
        path=f"{output_path}/{output_basename}.zip",
        store_name=output_basename,  # the shapefiles basename
        workspace=geosrv_workspace,
    )
    # print(r)
