# integrations/views.py

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .google_auth import get_flow, credentials_to_dict

@login_required
def google_auth(request):
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['google_auth_state'] = state
    return redirect(authorization_url)

@login_required
def google_auth_callback(request):
    state = request.session.get('google_auth_state')
    
    if not state:
        messages.error(request, 'State parameter missing.')
        return redirect(reverse('contacts:contact_list'))
    
    flow = get_flow()
    flow.fetch_token(code=request.GET.get('code'))

    credentials = flow.credentials
    request.session['google_credentials'] = credentials_to_dict(credentials)

    messages.success(request, 'Google account connected successfully.')
    
    # Redirect back to the email sending page
    return redirect(request.session.get('email_redirect_url', reverse('contacts:contact_list')))