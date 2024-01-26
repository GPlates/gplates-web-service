import os
import subprocess
from pathlib import Path

from django.conf import settings

__version__ = "0.1.9"

# download the plate models if the "model repo" directory does not exist.
if not os.path.isdir(settings.MODEL_REPO_DIR):
    Path(settings.MODEL_REPO_DIR).mkdir(parents=True, exist_ok=True)
    subprocess.call(["pmm", "download", "all", settings.MODEL_REPO_DIR])
