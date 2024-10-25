"""
WSGI config for cg_mobilization project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cg_mobilization.settings.production')

application = get_wsgi_application()
application = WhiteNoise(application, root=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media'))
application.add_files(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media'), prefix='media/')
