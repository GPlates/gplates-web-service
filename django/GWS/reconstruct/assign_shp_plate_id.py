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
from utils.fileio import (
    NoOutputFileError,
    find_and_unzip_all_zip_files,
    save_upload_files,
)
from utils.plate_model_utils import get_rotation_model, get_static_polygons


#
# reconstruct uploaded files
#
@csrf_exempt
def assign_plate_ids(request):
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
        with tempfile.TemporaryDirectory(prefix="gws-assign-plate-id-tmp") as tmp_dir:
            # save the upload files into the temporary dir
            save_upload_files(request, tmp_dir)

            # get parameters from the http post request
            model = request.POST.get("model", settings.MODEL_DEFAULT)

            rotation_model = get_rotation_model(model)

            # find and unzip all zip files
            find_and_unzip_all_zip_files(tmp_dir)

            reconstructable_files = glob.glob(f"{tmp_dir}/**/*.shp", recursive=True)

            # create output folder
            output_path = f"{tmp_dir}/output/"
            Path(output_path).mkdir(parents=True, exist_ok=True)

            for f in reconstructable_files:
                # print(f)
                features = pygplates.partition_into_plates(
                    get_static_polygons(model),
                    rotation_model,
                    f,
                    partition_method=pygplates.PartitionMethod.most_overlapping_plate,
                    properties_to_copy=[
                        pygplates.PartitionProperty.reconstruction_plate_id,
                        pygplates.PartitionProperty.valid_time_period,
                    ],
                )

                pygplates.FeatureCollection(features).write(
                    f"{output_path}/{os.path.basename(f)}-with-plate-ids.shp"
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
            ] = f"attachment; filename=shp-with-plate-ids.zip"

            return response
    except NoOutputFileError as e:
        e.print_error()
        return HttpResponseBadRequest(NoOutputFileError.error_msg)
    except:
        traceback.print_stack()
        traceback.print_exc(file=sys.stdout)
        err = traceback.format_exc()
        return HttpResponseServerError(err)
