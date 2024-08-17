from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import ComLog
from .forms import ComLogForm
from contacts.models import Church, People
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
import logging

class ComLogListView(ListView):
    model = ComLog
    template_name = 'com_log/com_log_list.html'
    context_object_name = 'com_logs'
    paginate_by = 20

    def get_queryset(self):
        return ComLog.objects.select_related('content_type').order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['com_logs'] = [
            {
                'id': log.id,
                'name': log.get_contact_name(),
                'type': log.get_contact_type(),
                'communication_type': log.get_communication_type_display(),
                'summary': log.summary,
                'date': log.date,
            }
            for log in context['com_logs']
        ]
        return context

class ComLogDetailView(DetailView):
    model = ComLog
    template_name = 'com_log/com_log_detail.html'
    context_object_name = 'com_log'

class ComLogCreateView(CreateView):
    model = ComLog
    form_class = ComLogForm
    template_name = 'com_log/com_log_form.html'
    success_url = reverse_lazy('com_log:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

class ComLogUpdateView(UpdateView):
    model = ComLog
    form_class = ComLogForm
    template_name = 'com_log/com_log_form.html'
    success_url = reverse_lazy('com_log:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

def contact_search(request):
    logger.debug(f"Contact search called with GET params: {request.GET}")
    
    contact_type = request.GET.get('type', '')
    search_term = request.GET.get('term', '')
    results = []

    logger.debug(f"Searching for {contact_type} with term: {search_term}")

    try:
        if contact_type == 'church':
            churches = Church.objects.filter(church_name__icontains=search_term)[:10]
            results = [{'id': church.id, 'name': church.church_name} for church in churches]
        elif contact_type == 'people':
            people = People.objects.filter(
                Q(first_name__icontains=search_term) | 
                Q(last_name__icontains=search_term)
            ).distinct()[:10]
            results = [{'id': person.id, 'name': f"{person.first_name} {person.last_name}"} for person in people]
        
        logger.debug(f"Found {len(results)} results")
        return JsonResponse(results, safe=False)
    except Exception as e:
        logger.error(f"Error in contact search: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)

    # This line should never be reached, but just in case:
    return HttpResponse("Unexpected error", status=500)