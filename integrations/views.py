# integrations/views.py

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from .google_auth import get_flow, credentials_to_dict
from google_auth_oauthlib.flow import Flow
from django.views.generic import TemplateView
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
import logging

logger = logging.getLogger(__name__)

def google_auth_flow(request):
    flow = Flow.from_client_config(
        client_config=settings.GOOGLE_CLIENT_CONFIG,
        scopes=[
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/gmail.modify'  # Added this scope
        ]
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    return flow

@login_required
def google_auth(request):
    flow = google_auth_flow(request)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    request.session['google_auth_state'] = state
    return redirect(authorization_url)

@login_required
def google_auth_callback(request):
    try:
        flow = google_auth_flow(request)
        flow.fetch_token(code=request.GET.get('code'))
        credentials = flow.credentials
        request.session['google_credentials'] = credentials_to_dict(credentials)
        messages.success(request, "Successfully authenticated with Google.")
        return redirect('task_tracker:task_list')
    except OAuth2Error as e:
        logger.error(f"OAuth2Error during Google authentication: {str(e)}")
        messages.error(request, "An error occurred during Google authentication. Please try again.")
    except Warning as w:
        # Log the warning but continue with the authentication process
        logger.warning(f"Warning during Google authentication: {str(w)}")
        messages.warning(request, "Authentication successful, but with a change in requested permissions.")
        return redirect('task_tracker:task_list')
    except Exception as e:
        logger.exception(f"Error during Google authentication: {str(e)}")
        messages.error(request, "An unexpected error occurred. Please try again.")
    return redirect('task_tracker:task_list')

class GoogleAuthSuccessView(TemplateView):
    template_name = 'integrations/google_auth_success.html'

    def get(self, request, *args, **kwargs):
        messages.success(request, 'Successfully authenticated with Google.')
        return_url = request.session.get('email_redirect_url')
        if return_url:
            del request.session['email_redirect_url']
            return redirect(return_url)
        return super().get(request, *args, **kwargs)