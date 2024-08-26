# google_auth.py

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Set up the OAuth 2.0 flow
CLIENT_CONFIG = {
    "web": {
        "client_id": "877634291388-70aa4mv47pomvt76r6jvlqkeaku1h2m8.apps.googleusercontent.com",
        "project_id": "crm-application-433417",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost:8000/google/auth/callback"]
    }
}

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_flow():
    return Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=CLIENT_CONFIG['web']['redirect_uris'][0]
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