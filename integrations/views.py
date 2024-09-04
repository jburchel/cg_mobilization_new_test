# integrations/views.py

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from .google_auth import get_flow, credentials_to_dict
from google_auth_oauthlib.flow import Flow
from django.views.generic import TemplateView

@login_required
def google_auth(request):
    flow = Flow.from_client_config(
        client_config=settings.GOOGLE_CLIENT_CONFIG,
        scopes=['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/calendar.events']
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
    state = request.session['google_auth_state']
    flow = Flow.from_client_config(
        client_config=settings.GOOGLE_CLIENT_CONFIG,
        scopes=['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/calendar.events'],
        state=state
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    try:
        flow.fetch_token(code=request.GET.get('code'))
        credentials = flow.credentials
        request.session['google_credentials'] = credentials_to_dict(credentials)
        
        request.user.google_refresh_token = credentials.refresh_token
        request.user.save()
        
        messages.success(request, 'Successfully authenticated with Google.')
        
        # Check if there's a pending task
        pending_task_id = request.session.pop('pending_task_id', None)
        if pending_task_id:
            task = Task.objects.get(id=pending_task_id)
            return redirect('task_tracker:task_create')
        
        return redirect(reverse('contacts:contact_list'))
    
    except Exception as e:       
        messages.error(request, f"Error during Google authentication: {str(e)}")
        return redirect(reverse('contacts:contact_list'))


class GoogleAuthSuccessView(TemplateView):
    template_name = 'integrations/google_auth_success.html'

    def get(self, request, *args, **kwargs):
        messages.success(request, 'Successfully authenticated with Google.')
        return_url = request.session.get('email_redirect_url')
        if return_url:
            del request.session['email_redirect_url']
            return redirect(return_url)
        return super().get(request, *args, **kwargs)