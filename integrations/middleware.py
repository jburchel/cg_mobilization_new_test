from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

class GoogleCredentialsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and 'google_credentials' in request.session:
            credentials_dict = request.session['google_credentials']
            credentials = Credentials(**credentials_dict)

            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    request.session['google_credentials'] = {
                        'token': credentials.token,
                        'refresh_token': credentials.refresh_token,
                        'token_uri': credentials.token_uri,
                        'client_id': credentials.client_id,
                        'client_secret': credentials.client_secret,
                        'scopes': credentials.scopes
                    }
                except Exception as e:
                    messages.error(request, "Failed to refresh Google credentials. Please re-authenticate.")
                    del request.session['google_credentials']
                    return redirect(reverse('integrations:google_auth'))

        response = self.get_response(request)
        return response