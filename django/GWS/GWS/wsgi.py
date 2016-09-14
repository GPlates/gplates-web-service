"""
WSGI config for GWS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

path = '/mnt/workspace/GWS/gplates-web/django/GWS/'
if path not in sys.path:
    sys.path.insert(0, path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GWS.settings")
    application = get_wsgi_application()



