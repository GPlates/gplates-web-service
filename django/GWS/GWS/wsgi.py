"""
WSGI config for GWS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os , sys

from django.core.wsgi import get_wsgi_application

paths = [
            '/usr/lib/pygplates/revision28',            
             os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        ]
for path in paths:
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GWS.settings")
application = get_wsgi_application()



