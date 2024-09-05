from .base import *
import os
from pathlib import Path

DEBUG = False

ALLOWED_HOSTS = ['mobilize.onrender.com']  # Add your domain

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Production-specific Google OAuth settings
GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
        "project_id": os.environ.get('GOOGLE_PROJECT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
        "redirect_uris": [os.environ.get('GOOGLE_REDIRECT_URI')]
    }
}

GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
GOOGLE_CALENDAR_CREDENTIALS_FILE = Path(os.getenv('GOOGLE_CREDENTIALS_FILE', '/opt/render/project/src/credentials_prod.json'))
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Additional security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your email provider's SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True

print(f"BASE_DIR: {BASE_DIR}")
print(f"STATIC_ROOT: {BASE_DIR / 'staticfiles'}")
print(f"MEDIA_ROOT: {BASE_DIR / 'media'}")
print(f"GOOGLE_CREDENTIALS_FILE: {os.getenv('GOOGLE_CREDENTIALS_FILE', 'Not set')}")
print(f"Current working directory: {os.getcwd()}")
print(f"Contents of current directory: {os.listdir('.')}")

# Only try to list /opt/render/project/src if it exists (i.e., in Render environment)
render_dir = Path('/opt/render/project/src')
if render_dir.exists():
    print(f"Contents of {render_dir}: {os.listdir(render_dir)}")
else:
    print(f"Directory {render_dir} does not exist (this is expected in local environment)")
    
print(f"STATIC_URL: {STATIC_URL}")
print(f"STATIC_ROOT: {STATIC_ROOT}")
print(f"STATICFILES_DIRS: {STATICFILES_DIRS}")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'task_tracker': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'integrations': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}