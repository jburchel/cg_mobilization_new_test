"""
WSGI config for cg_mobilization project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

path = '/home/cgmobilize/cg_mobilization'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cg_mobilization.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root='/opt/render/project/src/staticfiles')
application.add_files('/opt/render/project/src/media', prefix='media/')
