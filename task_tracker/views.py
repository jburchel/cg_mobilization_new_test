from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from .forms import TaskForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from contacts.models import Church, People
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from integrations.google_calendar import create_calendar_event, update_calendar_event, delete_calendar_event
from integrations.gmail import send_task_email
from integrations.utils import check_and_refresh_credentials
import logging

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class TaskListView(ListView):
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
class TaskDetailView(DetailView):
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
                from com_log.models import ComLog
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
        
        credentials = check_and_refresh_credentials(self.request)
        if not credentials:
            messages.warning(self.request, "Google integration is not set up. Please authenticate with Google.")
            return redirect('integrations:google_auth')

        calendar_event_id = create_calendar_event(self.request, self.object)
        if calendar_event_id:
            self.object.google_calendar_event_id = calendar_event_id
            self.object.save()
            messages.success(self.request, "Task created and added to Google Calendar.")
        else:
            messages.warning(self.request, "Task saved, but failed to add to Google Calendar. Please try again later.")

        email_sent = send_task_email(self.request, self.object)
        if email_sent:
            messages.success(self.request, "Email notification sent successfully.")
        else:
            messages.warning(self.request, "Failed to send email notification. Please check your email settings.")

        return response

@method_decorator(login_required, name='dispatch')    
class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_tracker/task_form.html'
    success_url = reverse_lazy('task_tracker:task_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        credentials = check_and_refresh_credentials(self.request)
        if credentials:
            if update_calendar_event(self.request, self.object):
                messages.success(self.request, "Task and Google Calendar event updated successfully.")
            else:
                messages.warning(self.request, "Task updated, but failed to update Google Calendar event.")
        else:
            messages.warning(self.request, "Google integration is not set up. Please authenticate with Google.")

        return response

@method_decorator(login_required, name='dispatch')
class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'task_tracker/task_confirm_delete.html'
    success_url = reverse_lazy('task_tracker:task_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        credentials = check_and_refresh_credentials(self.request)
        if credentials and self.object.google_calendar_event_id:
            if delete_calendar_event(request, self.object.google_calendar_event_id):
                messages.success(request, "Task and Google Calendar event deleted successfully.")
            else:
                messages.warning(request, "Task deleted, but failed to delete Google Calendar event.")
        elif not credentials:
            messages.warning(request, "Google integration is not set up. Please authenticate with Google.")

        return super().delete(request, *args, **kwargs)

@require_POST
@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Task.STATUS_CHOICES):
        task.status = new_status
        task.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
