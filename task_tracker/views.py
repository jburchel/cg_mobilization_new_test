from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from .forms import TaskForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from contacts.models import Church, People
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class TaskListView(ListView, LoginRequiredMixin):
    model = Task
    template_name = 'task_tracker/task_list.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_statuses'] = {
            'todo': Task.objects.filter(status='todo').order_by('due_date'),
            'in_progress': Task.objects.filter(status='in_progress').order_by('due_date'),
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
    success_url = reverse_lazy('task_tracker:task_list')  # Adjust this to your task list view

    def get_initial(self):
        initial = super().get_initial()
        contact_id = self.request.GET.get('contact_id')
        contact_type = self.request.GET.get('contact_type')
        
        if contact_id and contact_type:
            try:
                if contact_type == 'church':
                    contact = Church.objects.get(id=contact_id)
                elif contact_type == 'person':
                    contact = People.objects.get(id=contact_id)
                else:
                    contact = None
                
                if contact:
                    initial['contact'] = contact
                    initial['associated_contact'] = contact
            except (Church.DoesNotExist, People.DoesNotExist):
                pass
        
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
@method_decorator(login_required, name='dispatch')    
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_tracker/task_form.html'
    success_url = reverse_lazy('task_tracker:task_list')

@method_decorator(login_required, name='dispatch')
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task_tracker/task_confirm_delete.html'
    success_url = reverse_lazy('task_tracker:task_list')

@require_POST
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Task.STATUS_CHOICES):
        task.status = new_status
        task.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

