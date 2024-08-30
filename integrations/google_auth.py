# integrations/google_auth.py

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_flow():
    return Flow.from_client_config(
        client_config=settings.GOOGLE_CLIENT_CONFIG,
        scopes=['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/calendar.events'],
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def build_gmail_service(credentials):
    return build('gmail', 'v1', credentials=credentials)