import os
import subprocess
from pathlib import Path

from django.conf import settings

from .version import VERSION

__version__ = VERSION

# download the plate models if the "model repo" directory does not exist.
if not os.path.isdir(settings.MODEL_REPO_DIR):
    Path(settings.MODEL_REPO_DIR).mkdir(parents=True, exist_ok=True)
    subprocess.call(["pmm", "download", "all", settings.MODEL_REPO_DIR])
