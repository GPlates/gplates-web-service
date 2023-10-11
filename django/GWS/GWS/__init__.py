import os
import subprocess
from pathlib import Path

from django.conf import settings

__version__ = "1.0.0"

if not os.path.isdir(settings.MODEL_REPO_DIR):
    Path(settings.MODEL_REPO_DIR).mkdir(parents=True, exist_ok=True)
    subprocess.call(["pmm", "download", "all", settings.MODEL_REPO_DIR])
