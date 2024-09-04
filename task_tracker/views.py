from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from .forms import TaskForm
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from contacts.models import Church, People
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError
from integrations.google_calendar import get_calendar_service, create_calendar_event, update_calendar_event, delete_calendar_event
from django.conf import settings
import datetime
from django.utils import timezone
import os
import json
import logging

logger = logging.getLogger(__name__)

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

@method_decorator(login_required, name='dispatch')
class TaskListView(ListView, LoginRequiredMixin):
    model = Task
    template_name = 'task_tracker/task_list.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_statuses'] = {
            'todo': Task.objects.filter(status='todo').order_by('due_date'),
            'in progress': Task.objects.filter(status='in progress').order_by('due_date'),
            'review': Task.objects.filter(status='review').order_by('due_date'),
            'done': Task.objects.filter(status='done').order_by('due_date')
        }
        return context

@method_decorator(login_required, name='dispatch')    
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task_tracker/task_detail.html'
    context_object_name = 'task'

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_tracker/task_form.html'
    success_url = reverse_lazy('task_tracker:task_list')

    def get(self, request, *args, **kwargs):
        pending_task_id = request.session.pop('pending_task_id', None)
        if pending_task_id:
            task = Task.objects.get(id=pending_task_id)
            return self.form_valid(self.get_form_class()(instance=task))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        logger.info("TaskCreateView form_valid method called")
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        if 'google_credentials' not in self.request.session:
            logger.info("No Google credentials found. Redirecting to Google auth.")
            self.request.session['pending_task_id'] = self.object.id
            return redirect('integrations:google_auth')

        calendar_response = add_task_to_google_calendar(self.request, self.object)
        if isinstance(calendar_response, HttpResponseRedirect):
            logger.info("Redirecting to Google authorization")
            self.request.session['pending_task_id'] = self.object.id
            return calendar_response

        logger.info("Task created successfully")
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')    
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_tracker/task_form.html'
    success_url = reverse_lazy('task_tracker:task_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.update_google_calendar(self.object)
        return response

    def update_google_calendar(self, task):
        if task.google_calendar_event_id:
            try:
                service = get_calendar_service(self.request.session['google_credentials'])
                update_calendar_event(service, task)
            except KeyError:
                logger.warning('Google credentials not found. User may need to authenticate.')
                return redirect('task_tracker:initiate_google_auth')
            except HttpError as error:
                logger.error(f"Error updating Google Calendar event: {error}")
                # Handle the error (e.g., show a message to the user)

@method_decorator(login_required, name='dispatch')
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task_tracker/task_confirm_delete.html'
    success_url = reverse_lazy('task_tracker:task_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.google_calendar_event_id:
            try:
                service = get_calendar_service(self.request.session['google_credentials'])
                delete_calendar_event(service, self.object.google_calendar_event_id)
            except KeyError:
                logger.warning('Google credentials not found. User may need to authenticate.')
            except HttpError as error:
                logger.error(f"Error deleting Google Calendar event: {error}")
                # Handle the error (e.g., show a message to the user)
        return super().delete(request, *args, **kwargs)

@require_POST
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Task.STATUS_CHOICES):
        task.status = new_status
        task.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def add_task_to_google_calendar(request, task):
    logger.info("Starting Google Calendar integration")

    if not settings.GOOGLE_CALENDAR_CREDENTIALS_FILE:
        logger.warning("Google Calendar credentials file not set. Skipping calendar integration.")
        return

    if not os.path.exists(settings.GOOGLE_CALENDAR_CREDENTIALS_FILE):
        logger.error(f"Credentials file not found: {settings.GOOGLE_CALENDAR_CREDENTIALS_FILE}")
        return

    try:
        with open(settings.GOOGLE_CALENDAR_CREDENTIALS_FILE, 'r') as f:
            client_config = json.load(f)

        # Handle the due_date
        if task.due_date:
            # Convert to UTC
            due_date = task.due_date.astimezone(datetime.timezone.utc)
        else:
            due_date = timezone.now().astimezone(datetime.timezone.utc)

        # Format the date-time string correctly for Google Calendar API
        formatted_date = due_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        
        logger.info(f"Formatted date for Google Calendar: {formatted_date}")

        if 'web' not in client_config:
            logger.error("Invalid client config. 'web' key not found.")
            return

        credentials = Credentials(**request.session['google_credentials'])

        if not credentials.valid:
            logger.info("Credentials not valid, refreshing")
            if credentials.expired and credentials.refresh_token:
                request_adapter = Request()
                credentials.refresh(request_adapter)
                # Update session with refreshed credentials
                request.session['google_credentials'] = credentials_to_dict(credentials)
            else:
                logger.info("Credentials expired and can't be refreshed, starting new auth flow")
                return redirect('task_tracker:initiate_google_auth')

        logger.info("Building calendar service")
        service = build('calendar', 'v3', credentials=credentials)

        event = {
            'summary': task.title,
            'description': task.description,
            'start': {
                'dateTime': formatted_date,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (due_date + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S%z'),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [],
            },
        }

        # Add reminder
        reminder_minutes = 30  # default to 30 minutes
        if task.reminder == 'custom':
            reminder_minutes = task.custom_reminder
        elif task.reminder == '15_min':
            reminder_minutes = 15
        elif task.reminder == '30_min':
            reminder_minutes = 30
        elif task.reminder == '1_hour':
            reminder_minutes = 60
        elif task.reminder == '2_hours':
            reminder_minutes = 120
        elif task.reminder == '1_