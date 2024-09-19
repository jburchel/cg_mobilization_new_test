from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import logging

logger = logging.getLogger(__name__)

def check_and_refresh_credentials(request):
    credentials_dict = request.session.get('google_credentials')
    if not credentials_dict:
        logger.error("Google credentials not found in session")
        return None

    credentials = Credentials(**credentials_dict)
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                request.session['google_credentials'] = credentials_to_dict(credentials)
                logger.info("Credentials refreshed successfully")
            except RefreshError:
                logger.error("Failed to refresh credentials")
                return None
        else:
            logger.error("Credentials expired and can't be refreshed")
            return None

    return credentials

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }