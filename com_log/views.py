from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import CommunicationLog
from .forms import CommunicationLogForm
from django.urls import reverse

class CommunicationLogListView(ListView):
    model = CommunicationLog
    template_name = 'com_log/com_log_list.html'
    context_object_name = 'com_logs'
    paginate_by = 20

    def get_queryset(self):
        return CommunicationLog.objects.select_related('content_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['com_logs'] = [
            {
                'id': log.id,
                'name': log.get_contact_name(),
                'type': log.content_type.model.capitalize(),
                'communication_type': log.get_communication_type_display(),
                'summary': log.summary,
                'date': log.date,
            }
            for log in context['com_logs']

        ]
        return context
    
class CommunicationLogDetailView(DetailView):
    model = CommunicationLog
    template_name = 'com_log/com_log_detail.html'
    context_object_name = 'log'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_name'] = self.object.get_contact_name()
        context['contact_type'] = self.object.content_type.model.capitalize()
        return context

class AddComLogView(CreateView):
    form_class = CommunicationLogForm
    template_name = 'com_log/com_log_form.html'
    success_url = reverse_lazy('com_log:com_log_list')

    def get_initial(self):
        initial = super().get_initial()
        initial['contact_type'] = self.request.POST.get('contact_type')
        return initial
   
    def form_valid(self, form):
        response = super().form_valid(form)
        # You can add a success message here if you want
        return response

class EditComLogView(UpdateView):
    model = CommunicationLog
    template_name = 'com_log/com_log_form.html'
    form_class = CommunicationLogForm
    success_url = reverse_lazy('com_log:edit_com_log' + '<int:pk>/edit')

    def get(self, request, pk):
        com_log = CommunicationLog.objects.get(pk=pk)
        form = self.form_class(instance=com_log)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        com_log = CommunicationLog.objects.get(pk=pk)
        form = self.form_class(request.POST, instance=com_log)
        if form.is_valid():
            com_log = form.save()
            messages.success(request, 'Communication log updated successfully.')
            return redirect('com_log:com_log_detail', pk=com_log.pk)
        return render(request, self.template_name, {'form': form})
