from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from .forms import TaskForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

class TaskListView(ListView):
    model = Task
    template_name = 'task_tracker/task_list.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_statuses'] = {
            'todo': Task.objects.filter(status='todo'),
            'in_progress': Task.objects.filter(status='in_progress'),
            'review': Task.objects.filter(status='review'),
            'done': Task.objects.filter(status='done')
        }
        return context
    
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task_tracker/task_detail.html'
    context_object_name = 'task'

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_tracker/task_form.html'
    success_url = reverse_lazy('task_tracker:task_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_tracker/task_form.html'
    success_url = reverse_lazy('task_tracker:task_list')

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

