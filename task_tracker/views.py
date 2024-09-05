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

logger = logging.getLogger(__name__)

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_tracker/task_form.html'
    success_url = reverse_lazy('task_tracker:task_list')

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        pending_task_id = request.session.pop('pending_task_id', None)
        if pending_task_id:
            try:
                task = Task.objects.get(id=pending_task_id)
                form = self.get_form_class()(instance=task)
                return self.render_to_response(self.get_context_data(form=form, task=task))
            except Task.DoesNotExist:
                logger.warning(f"Pending task with id {pending_task_id} not found")
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        logger.info("TaskCreateView form_valid method called")
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        if 'google_credentials' not in self.request.session:
            logger.info("No Google credentials found. Redirecting to Google auth.")
            self.request.session['pending_task_id'] = self.object.id
            return redirect('integrations:google_auth')

        result = self.add_task_to_google_calendar(self.request, self.object)
        if not result:
            # If calendar integration failed, we should still save the task
            messages.warning(self.request, "Task saved, but failed to add to Google Calendar. Please try again later.")
        return super().form_valid(form)

    def add_task_to_google_calendar(self, request, task):
        logger.info(f"Attempting to add task {task.id} to Google Calendar")
        try:
            credentials_dict = request.session['google_credentials']
            logger.info(f"Credentials from session: {json.dumps(credentials_dict, indent=2)}")
            
            credentials = Credentials(**credentials_dict)
            logger.info("Credentials object created")
            
            if credentials.expired and credentials.refresh_token:
                logger.info("Credentials expired. Attempting to refresh.")
                credentials.refresh(Request())
                # Update the session with refreshed credentials
                request.session['google_credentials'] = credentials_to_dict(credentials)
                logger.info("Credentials refreshed and updated in session")
            
            service = get_calendar_service(credentials)
            logger.info("Calendar service created")
            
            event_id = create_calendar_event(service, task)
            logger.info(f"create_calendar_event returned: {event_id}")
            if event_id:
                task.google_calendar_event_id = event_id
                task.save()
                logger.info(f"Successfully added task {task.id} to Google Calendar with event_id {event_id}")
                return True
            else:
                logger.error(f"Failed to create event for task {task.id}")
                return False
        except KeyError as e:
            logger.error(f"KeyError in add_task_to_google_calendar: {str(e)}")
        except RefreshError as e:
            logger.error(f"RefreshError: {str(e)}. User may need to re-authenticate.")
            # Clear the invalid credentials from the session
            request.session.pop('google_credentials', None)
            return False
        except Exception as e:
            logger.exception(f"Error adding task {task.id} to Google Calendar: {str(e)}")
        return False
    def get_context_data(self, **kwargs):
        context = {}
        if 'form' not in kwargs:
            context['form'] = self.get_form()
        else:
            context['form'] = kwargs['form']
        if 'task' in kwargs:
            context['task'] = kwargs['task']
        return context

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

def add_task_to_google_calendar(self, request, task):
    logger.info(f"Attempting to add task {task.id} to Google Calendar")
    try:
        credentials = Credentials(**request.session['google_credentials'])
        logger.info("Credentials retrieved from session")
        service = get_calendar_service(request.session['google_credentials'])
        logger.info("Calendar service created")
        
        event_id = create_calendar_event(service, task)
        logger.info(f"create_calendar_event returned: {event_id}")
        if event_id:
            task.google_calendar_event_id = event_id
            task.save()
            logger.info(f"Successfully added task {task.id} to Google Calendar with event_id {event_id}")
        else:
            logger.error(f"Failed to create event for task {task.id}")
    except KeyError as e:
        logger.error(f"KeyError in add_task_to_google_calendar: {str(e)}")
    except Exception as e:
        logger.exception(f"Error adding task {task.id} to Google Calendar: {str(e)}")

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
        except HttpError as error:
            if error.resp.status == 401:
                logger.error("Authentication Error: Credentials might be expired")
                return redirect('task_tracker:initiate_google_auth')
            elif error.resp.status == 400:
                logger.error(f"Bad Request Error: {error.content}")
                # Handle the bad request error (e.g., invalid event data)
            else:
                logger.error(f"Google Calendar API Error: {error}")
            # You might want to set a flag or message to inform the user that the calendar event creation failed

    except Exception as e:
        logger.exception(f"Unexpected error in Google Calendar integration: {str(e)}")

    return None  # If we get here, no redirection was needed

# ... (other views and functions remain the same)