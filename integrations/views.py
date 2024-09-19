from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .google_auth import get_flow, credentials_to_dict
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .utils import check_and_refresh_credentials
import logging

logger = logging.getLogger(__name__)

@login_required
def google_auth(request):
    flow = Flow.from_client_config(
        client_config=settings.GOOGLE_CLIENT_CONFIG,
        scopes=[
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    request.session['google_auth_state'] = state
    return redirect(authorization_url)

@login_required
def google_auth_callback(request):
    state = request.session.get('google_auth_state')
    if not state:
        messages.error(request, "Invalid state parameter. Please try authenticating again.")
        return redirect('integrations:settings')

    flow = Flow.from_client_config(
        client_config=settings.GOOGLE_CLIENT_CONFIG,
        scopes=[
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/gmail.modify'
        ],
        state=state
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    try:
        flow.fetch_token(code=request.GET.get('code'))
        credentials = flow.credentials
        request.session['google_credentials'] = credentials_to_dict(credentials)
        messages.success(request, "Successfully authenticated with Google.")
    except Exception as e:
        logger.error(f"Error during Google authentication: {str(e)}")
        messages.error(request, "An error occurred during Google authentication. Please try again.")

    return redirect('integrations:settings')

@login_required
def settings_view(request):
    context = {
        'is_authenticated': 'google_credentials' in request.session
    }

    if context['is_authenticated']:
        try:
            credentials = Credentials(**request.session['google_credentials'])
            gmail_service = build('gmail', 'v1', credentials=credentials)
            profile = gmail_service.users().getProfile(userId='me').execute()
            context['email'] = profile['emailAddress']
        except Exception as e:
            logger.error(f"Error fetching Gmail profile: {str(e)}")
            context['email'] = "Unable to fetch email address"

    return render(request, 'integrations/settings.html', context)

@login_required
def test_integration(request):
    credentials = check_and_refresh_credentials(request)
    if not credentials:
        messages.error(request, "Google credentials are missing or invalid. Please authenticate again.")
        return redirect('integrations:settings')

    try:
        # Test Gmail
        gmail_service = build('gmail', 'v1', credentials=credentials)
        gmail_profile = gmail_service.users().getProfile(userId='me').execute()
        messages.success(request, f"Gmail integration is working. Connected email: {gmail_profile['emailAddress']}")

        # Test Google Calendar
        calendar_service = build('calendar', 'v3', credentials=credentials)
        calendar_list = calendar_service.calendarList().list().execute()
        messages.success(request, f"Google Calendar integration is working. Found {len(calendar_list['items'])} calendars.")

    except HttpError as error:
        messages.error(request, f"An error occurred while testing the integration: {error}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")

    return redirect('integrations:settings')

@login_required
def revoke_access(request):
    if 'google_credentials' in request.session:
        credentials = Credentials(**request.session['google_credentials'])
        try:
            credentials.revoke(request)
            messages.success(request, "Google access has been successfully revoked.")
        except Exception as e:
            logger.error(f"Error revoking Google access: {str(e)}")
            messages.error(request, "An error occurred while revoking Google access. Please try again.")
    else:
        messages.info(request, "No active Google integration found.")

    if 'google_credentials' in request.session:
        del request.session['google_credentials']

    return redirect('integrations:settings')