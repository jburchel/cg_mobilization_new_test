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
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cg_mobilization.settings.production')

application = get_wsgi_application()

static_root = '/opt/render/project/src/staticfiles'
application = WhiteNoise(application, root=settings.STATIC_ROOT)
application.add_files(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), prefix='static/')
application.add_files(settings.STATIC_ROOT, prefix="static/")

media_root = '/opt/render/project/src/media'
application.add_files('/opt/render/project/src/media', prefix='media/')

import logging
logger = logging.getLogger(__name__)
logger.info(f"Static root path: {static_root}")
logger.info(f"Media root path: {media_root}")
