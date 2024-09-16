from .base import *
import os
from dotenv import load_dotenv

load_dotenv()



DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development-specific Google OAuth settings
GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": "47896425604-ggcf0g4vboomcg0g78tir7o8d0j7i9qn.apps.googleusercontent.com",
        "project_id": "mobilize-crm-dev",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost:8000/integrations/google/auth/callback/"]
    }
}

GOOGLE_REDIRECT_URI = "http://localhost:8000/integrations/google/auth/callback/"
GOOGLE_CALENDAR_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials_dev.json')
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Use console email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False