import io
import os
import sys
import traceback
import zipfile

import pygplates
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from utils.get_model import get_reconstruction_model_dict
from pathlib import Path
import tempfile, glob

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
            print(tmp_dir)

            # save the upload files into the temporary dir
            save_upload_files(request, tmp_dir)

            # get parameters from the http post request
            time, model, assign_plate_id_flag = get_request_parameters(request)

            reconstructable_files = []
            reconstructable_files = glob.glob(f"{tmp_dir}/**/*.shp", recursive=True)
            print(reconstructable_files)
            # (name, ext) = os.path.splitext(f.name)
            # if ext in [".shp", ".gpml", ".gpmlz"]:
            # reconstructable_files.append(f.name)

            model_dict = get_reconstruction_model_dict(model)
            if not model_dict:
                return HttpResponseBadRequest(
                    f'The "model" ({model}) cannot be recognized.'
                )

            rotation_model = pygplates.RotationModel(
                [
                    f"{settings.MODEL_STORE_DIR}/{model}/{rot_file}"
                    for rot_file in model_dict["RotationFile"]
                ]
            )

            static_polygons_filename = (
                f'{settings.MODEL_STORE_DIR}/{model}/{model_dict["StaticPolygons"]}'
            )

            # create output folder
            output_path = f"{tmp_dir}/output/"
            Path(output_path).mkdir(parents=True, exist_ok=True)

            assign_plate_id_flag = True
            if assign_plate_id_flag:
                feature_collection = pygplates.FeatureCollection()
                for f in reconstructable_files:
                    # print(f)
                    features = pygplates.partition_into_plates(
                        static_polygons_filename,
                        rotation_model,
                        f,
                        partition_method=pygplates.PartitionMethod.most_overlapping_plate,
                        properties_to_copy=[
                            pygplates.PartitionProperty.reconstruction_plate_id,
                            pygplates.PartitionProperty.valid_time_period,
                        ],
                    )

                    feature_collection.add(features)

                pygplates.reconstruct(
                    feature_collection,
                    rotation_model,
                    f"{output_path}/reconstructed-{time}Ma.shp",
                    float(time),
                )
            else:  # when assign_plate_id_flag = False
                print(reconstructable_files)
                print(f"{output_path}/reconstructed-{time}Ma.shp")
                pygplates.reconstruct(
                    reconstructable_files,
                    rotation_model,
                    f"{output_path}/reconstructed-{time}Ma.shp",
                    float(time),
                )

            # print(os.listdir(output_path))
            s = io.BytesIO()
            with zipfile.ZipFile(s, "w") as zf:
                for r, d, files in os.walk(output_path):
                    if not files:
                        return HttpResponseServerError(
                            "Error: No output files have been created!"
                        )
                    for f in files:
                        print(os.path.join(r, f))
                        zf.write(str(os.path.join(r, f)), f)

            response = HttpResponse(
                s.getvalue(), content_type="application/x-zip-compressed"
            )
            response[
                "Content-Disposition"
            ] = "attachment; filename=reconstructed_files.zip"

            return response
    except:
        traceback.print_stack()
        traceback.print_exc(file=sys.stdout)
        err = traceback.format_exc()
        return HttpResponseBadRequest(err)


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


# save the files into the temporary dir
def save_upload_files(request, tmp_dir):
    for fs in request.FILES.lists():
        for f in fs[1]:
            print((f.name))

            with open(f"{tmp_dir}/{f.name}", "wb+") as fp:
                for chunk in f.chunks():
                    fp.write(chunk)


# get parameters from the http post request
def get_request_parameters(request):
    time = request.POST.get("time", None)
    model = request.POST.get("model", settings.MODEL_DEFAULT)
    assign_plate_id_flag = request.POST.get("assign_plate_id", False)
    try:
        if 1 == int(assign_plate_id_flag):
            assign_plate_id_flag = True
    except:
        pass  # do nothing, the default assign_plate_id_flag is False
    return time, model, assign_plate_id_flag
