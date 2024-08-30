from .base import *
import os

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
        "redirect_uris": ["https://mobilize.onrender.com/integrations/google/auth/callback/"]
    }
}

GOOGLE_REDIRECT_URI = "https://mobilize.onrender.com/integrations/google/auth/callback/"
GOOGLE_CALENDAR_CREDENTIALS_FILE = BASE_DIR / 'credentials_prod.json'
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Additional security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True