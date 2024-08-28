# integrations/views.py

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from .google_auth import get_flow, credentials_to_dict
from google_auth_oauthlib.flow import Flow

@login_required
def google_auth(request):
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['google_auth_state'] = state
    request.session['email_redirect_url'] = request.GET.get('next', reverse('contacts:contact_list'))
    return redirect(authorization_url)

@login_required
def google_auth_callback(request):
    flow = get_flow()
    
    try:
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
        request.session['google_credentials'] = credentials_to_dict(credentials)
        messages.success(request, 'Google account connected successfully.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    
    return redirect(request.session.get('email_redirect_url', reverse('contacts:contact_list')))