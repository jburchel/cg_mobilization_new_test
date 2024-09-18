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
from django.contrib import messages
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
from google.auth.exceptions import RefreshError

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

    def get_initial(self):
        initial = super().get_initial()
        if 'com_log_id' in self.request.GET:
            com_log_id = self.request.GET.get('com_log_id')
            try:
                com_log = ComLog.objects.get(id=com_log_id)
                initial['title'] = f"Follow-up: {com_log.get_contact_name()}"
                initial['description'] = f"Follow-up on communication: {com_log.notes[:100]}..."
                initial['associated_contact'] = com_log.contact
            except ComLog.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'com_log_id' in self.request.GET:
            context['from_com_log'] = True
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        if 'google_credentials' not in self.request.session:
            self.request.session['pending_task_id'] = self.object.id
            return redirect('integrations:google_auth')

        result = add_task_to_google_calendar(self.request, self.object)
        if not result:
            messages.warning(self.request, "Task saved, but failed to add to Google Calendar. Please try again later.")
        else:
            messages.success(self.request, "Task created and added to Google Calendar.")
        return response

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
    logger.info(f"Attempting to add task {task.id} to Google Calendar")
    try:
        credentials_dict = request.session.get('google_credentials')
        if not credentials_dict:
            logger.error("Google credentials not found in session")
            return False
        
        logger.info(f"Credentials from session: {json.dumps(credentials_dict, indent=2)}")
        
        service = get_calendar_service(credentials_dict)
        logger.info("Calendar service created")
        
        event_id = create_calendar_event(service, task)
        logger.info(f"create_calendar_event returned: {event_id}")
        if event_id:
            task.google_calendar_event_id = event_id
            task.save()
            logger.info(f"Task {task.id} updated with Google Calendar event ID: {event_id}")
            return True
        else:
            logger.error(f"Failed to create event for task {task.id}")
            return False
    except KeyError as e:
        logger.error(f"KeyError in add_task_to_google_calendar: {str(e)}")
    except Exception as e:
        logger.exception(f"Error adding task {task.id} to Google Calendar: {str(e)}")

        credentials = Credentials(**request.session.get('google_credentials', {}))
        if not credentials.valid:
            logger.info("Credentials not valid, refreshing")
            if credentials.expired and credentials.refresh_token:
                request_adapter = Request()
                credentials.refresh(request_adapter)
                # Update session with refreshed credentials
                request.session['google_credentials'] = credentials_to_dict(credentials)
            else:
                logger.info("Credentials expired and can't be refreshed, starting new auth flow")
                return False

        logger.info("Building calendar service")
        service = build('calendar', 'v3', credentials=credentials)

        formatted_date = task.due_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        due_date = task.due_date

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
        elif task.reminder == '1_day':
            reminder_minutes = 1440

        event['reminders']['overrides'].append({
            'method': 'popup',
            'minutes': reminder_minutes
        })

        logger.info(f"Inserting event into calendar: {event}")
        try:
            event = service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f'Event created: {event.get("htmlLink")}')
            task.google_calendar_event_id = event['id']
            task.save()
            return True
        except HttpError as error:
            if error.resp.status == 401:
                logger.error("Authentication Error: Credentials might be expired")
                return False
            elif error.resp.status == 400:
                logger.error(f"Bad Request Error: {error.content}")
                # Handle the bad request error (e.g., invalid event data)
            else:
                logger.error(f"Google Calendar API Error: {error}")
            return False

    return False  # If we get here, an error occurred