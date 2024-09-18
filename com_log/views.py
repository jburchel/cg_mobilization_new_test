from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ComLog
from django.contrib import messages
from .forms import ComLogForm
from contacts.models import Church, People
from django.http import JsonResponse, Http404
from django.db.models import Q
import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin

logger = logging.getLogger(__name__)
@method_decorator(login_required, name='dispatch')
class ComLogListView(ListView):
    model = ComLog
    template_name = 'com_log/com_log_list.html'
    context_object_name = 'com_logs'
    paginate_by = 10

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
                'notes': log.notes,
                'date': log.date,
            }
            for log in context['com_logs']
        ]
        return context
    
@method_decorator(login_required, name='dispatch')
class ComLogDetailView(DetailView, LoginRequiredMixin):
    model = ComLog
    template_name = 'com_log/com_log_detail.html'
    context_object_name = 'com_log'
    
@method_decorator(login_required, name='dispatch')
class ComLogCreateView(CreateView):
    model = ComLog
    form_class = ComLogForm
    template_name = 'com_log/com_log_form.html'
    success_url = reverse_lazy('com_log:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        contact = form.cleaned_data['contact']
        
        if isinstance(contact, People):
            content_type = ContentType.objects.get_for_model(People)
        elif isinstance(contact, Church):
            content_type = ContentType.objects.get_for_model(Church)
        else:
            # Handle other contact types if necessary
            content_type = ContentType.objects.get_for_model(contact.__class__)
        
        self.object.content_type = content_type
        self.object.object_id = contact.id
        self.object.save()
        
        messages.success(self.request, 'Communication log added successfully.')
        return super().form_valid(form)

def contact_search(request):
    contact_type = request.GET.get('type')
    query = request.GET.get('term', '')
    logger.info(f"Contact search: type={contact_type}, query={query}")

    results = []

    if contact_type == 'church':
        churches = Church.objects.filter(church_name__icontains=query)[:10]
        results = [{'id': church.id, 'value': church.church_name, 'label': church.church_name} for church in churches]
    elif contact_type == 'person':
        people = People.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )[:10]
        results = [{'id': person.id, 'value': f"{person.first_name} {person.last_name}", 'label': f"{person.first_name} {person.last_name}"} for person in people]

    logger.info(f"Contact search results: {results}")
    return JsonResponse(results, safe=False)

@method_decorator(login_required, name='dispatch')
class ComLogUpdateView(SuccessMessageMixin, UpdateView):
    model = ComLog
    form_class = ComLogForm
    template_name = 'com_log/com_log_form.html'
    success_message = "Communication log was updated successfully"

    def get_success_url(self):
        return reverse_lazy('com_log:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object:
            contact = self.object.contact
            if isinstance(contact, People):
                contact_name = f"{contact.first_name} {contact.last_name}"
                contact_type = 'person'
            elif isinstance(contact, Church):
                contact_name = contact.church_name
                contact_type = 'church'
            else:
                contact_name = str(contact)
                contact_type = 'unknown'

            kwargs['initial'] = {
                'contact_type': contact_type,
                'contact': contact_name,
                'contact_id': contact.id,
                'communication_type': self.object.communication_type,
                'notes': self.object.notes,
            }
        return kwargs
    
@method_decorator(login_required, name='dispatch')
class ContactInteractionsListView(ListView):
    template_name = 'com_log/contact_interactions_list.html'
    context_object_name = 'interactions'

    def get_queryset(self):
        contact_type = self.kwargs['contact_type']
        contact_id = self.kwargs['contact_id']
        
        if contact_type == 'person':
            contact = get_object_or_404(People, id=contact_id)
        elif contact_type == 'church':
            contact = get_object_or_404(Church, id=contact_id)
        else:
            raise Http404("Invalid contact type")
        
        content_type = ContentType.objects.get_for_model(contact)
        return ComLog.objects.filter(
            content_type=content_type,
            object_id=contact.id
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contact_type = self.kwargs['contact_type']
        contact_id = self.kwargs['contact_id']
        
        if contact_type == 'person':
            context['contact'] = get_object_or_404(People, id=contact_id)
        elif contact_type == 'church':
            context['contact'] = get_object_or_404(Church, id=contact_id)
        
        return context
