from django.views.generic import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .forms import PeopleForm, ChurchForm, EmailForm
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Contact, Church, People
from django.db.models import Count 
from com_log.models import ComLog
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers.json import DjangoJSONEncoder
import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64


logger = logging.getLogger(__name__)
@method_decorator(login_required, name='dispatch')
class ContactListView(ListView):
    model = Contact
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        return Contact.objects.select_related('people', 'church').order_by('last_name', 'first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contacts_data = []
        
        for contact in context['contacts']:
            contact_dict = {
                'id': contact.id,
                'name': contact.get_name(),
                'type': 'Person' if hasattr(contact, 'people') else 'Church',
                'email': contact.email,
                'phone': contact.phone,
                'last_contact': contact.date_modified.strftime('%Y-%m-%d') if contact.date_modified else ''
            }
            
            if hasattr(contact, 'people'):
                people = contact.people
                contact_dict['person_type'] = people.person_type if hasattr(people, 'person_type') else ''
            else:
                contact_dict['person_type'] = ''
            
            contacts_data.append(contact_dict)
        
        context['contacts_json'] = json.dumps(contacts_data)
        return context
    
@login_required
def add_contact(request, contact_type):
    if contact_type not in ['people', 'church']:
        messages.error(request, 'Invalid contact type.')
        return redirect('contacts:contact_list')

    if request.method == 'POST':
        if contact_type == 'people':
            form = PeopleForm(request.POST)
        else:
            form = ChurchForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, f'New {contact_type} contact added successfully!')
            return redirect('contacts:contact_list')
    else:
        if contact_type == 'people':
            form = PeopleForm()
        else:
            form = ChurchForm()

    return render(request, 'contacts/add_contact.html', {'form': form, 'contact_type': contact_type})

@login_required
def edit_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    
    if hasattr(contact, 'church'):
        model = Church
        form_class = ChurchForm
        instance = contact.church
    elif hasattr(contact, 'people'):
        model = People
        form_class = PeopleForm
        instance = contact.people
    else:
        messages.error(request, 'Invalid contact type.')
        return redirect('contacts:contact_list')
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model.__name__} updated successfully!')
            return redirect('contacts:contact_list')
    else:
        form = form_class(instance=instance)
    
    context = {
        'form': form,
        'contact': instance,
        'contact_type': model.__name__.lower()
    }
    return render(request, 'contacts/edit_contact.html', context)
@method_decorator(login_required, name='dispatch')
class ChurchListView(ListView, LoginRequiredMixin):
    model = Church
    template_name = 'contacts/church_list.html'
    context_object_name = 'churches'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        churches = self.get_queryset()
        total_churches = churches.count()

        pipeline_choices = dict(Church.CHURCH_PIPELINE_CHOICES)
        pipeline_summary = dict(churches.values_list('church_pipeline').annotate(count=Count('church_pipeline')))
        
        # Ensure all stages are included, even if count is zero
        for key, value in pipeline_choices.items():
            if value not in pipeline_summary:
                pipeline_summary[value] = 0

        # Create a list of tuples (stage, count) in the order of CHURCH_PIPELINE_CHOICES
        sorted_summary = [(pipeline_choices[key], pipeline_summary[pipeline_choices[key]]) 
                          for key, _ in Church.CHURCH_PIPELINE_CHOICES]
        
        # Insert total at the beginning
        sorted_summary.insert(0, ('Total', total_churches))

        context['pipeline_summary'] = sorted_summary
        context['pipeline_stages'] = {stage: churches.filter(church_pipeline=key) 
                                      for key, stage in pipeline_choices.items()}

        return context
    
@require_POST
@csrf_exempt
def update_church_pipeline_stage(request):
    data = json.loads(request.body)
    church_id = data.get('church_id')
    new_stage = data.get('new_stage')
    
    try:
        church = Church.objects.get(id=church_id)
        new_stage_db_value = next((key for key, value in Church.CHURCH_PIPELINE_CHOICES if value.lower().replace(' ', '-') == new_stage.lower()), None)
        
        if new_stage_db_value is None:
            return JsonResponse({'success': False, 'error': f'Invalid stage: {new_stage}'}, status=400)
        
        church.church_pipeline = new_stage_db_value
        church.save()
        return JsonResponse({'success': True})
    except Church.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Church not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@method_decorator(login_required, name='dispatch')    
class ChurchDetailView(DetailView, LoginRequiredMixin):
    model = Church
    template_name = 'contacts/church_detail.html'
    context_object_name = 'church'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        church_content_type = ContentType.objects.get_for_model(Church)
        context['recent_communications'] = ComLog.objects.filter(
            content_type=church_content_type,
            object_id=self.object.id
        ).order_by('-date_created')[:3]
        return context
@method_decorator(login_required, name='dispatch')    
class ChurchAddView(LoginRequiredMixin, CreateView):
    model = Church
    form_class = ChurchForm
    template_name = 'contacts/add_contact.html'
    success_url = reverse_lazy('contacts:church_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_type'] = 'church'
        return context

    def form_valid(self, form):
        # You can add any additional logic here before saving the form
        return super().form_valid(form)
@method_decorator(login_required, name='dispatch')
class ChurchUpdateView(UpdateView, LoginRequiredMixin):
    model = Church
    form_class = ChurchForm
    template_name = 'contacts/edit_contact.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)            
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_type'] = 'church'
        return context

    def get_success_url(self):
        return reverse_lazy('contacts:church_detail', kwargs={'pk': self.object.pk})
@method_decorator(login_required, name='dispatch')
class PeopleListView(ListView, LoginRequiredMixin):
    model = People
    template_name = 'contacts/people_list.html'
    context_object_name = 'people'
    ordering = ['last_name', 'first_name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        people = self.get_queryset()
        total_people = people.count()

        pipeline_choices = dict(People.PEOPLE_PIPELINE)
        
        # Create pipeline_stages first
        pipeline_stages = {stage: people.filter(people_pipeline=key) for key, stage in pipeline_choices.items()}
        
        # Calculate pipeline_summary based on pipeline_stages
        pipeline_summary = {stage: queryset.count() for stage, queryset in pipeline_stages.items()}
        
        # Debug information
        context['debug_pipeline_choices'] = pipeline_choices
        context['debug_pipeline_summary'] = pipeline_summary

        # Convert to list and sort by the order in PEOPLE_PIPELINE
        sorted_summary = sorted(
            pipeline_summary.items(),
            key=lambda x: list(pipeline_choices.values()).index(x[0])
        )

        # Add total to the beginning of the summary
        sorted_summary.insert(0, ('Total', total_people))

        context['pipeline_summary'] = sorted_summary
        context['pipeline_stages'] = pipeline_stages

        # More debug information
        context['debug_sorted_summary'] = sorted_summary
        context['debug_pipeline_stages'] = {stage: list(queryset.values_list('id', flat=True)) for stage, queryset in pipeline_stages.items()}

        return context
    
@require_POST
@csrf_exempt
def update_pipeline_stage(request):
    data = json.loads(request.body)
    person_id = data.get('person_id')
    new_stage = data.get('new_stage')
    
    try:
        person = People.objects.get(id=person_id)
        # Find the matching database value for the new stage
        new_stage_db_value = next((key for key, value in People.PEOPLE_PIPELINE if value.lower().replace(' ', '-') == new_stage.lower()), None)
        
        if new_stage_db_value is None:
            return JsonResponse({'success': False, 'error': f'Invalid stage: {new_stage}'}, status=400)
        
        person.people_pipeline = new_stage_db_value
        person.save()
        return JsonResponse({'success': True})
    except People.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Person not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@method_decorator(login_required, name='dispatch')    
class PersonAddView(LoginRequiredMixin, CreateView):
    model = People
    form_class = PeopleForm
    template_name = 'contacts/add_contact.html'
    success_url = reverse_lazy('contacts:people_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_type'] = 'person'
        return context

    def form_valid(self, form):
        # You can add any additional logic here before saving the form
        return super().form_valid(form)
@method_decorator(login_required, name='dispatch')
class PersonUpdateView(UpdateView, LoginRequiredMixin):
    model = People
    form_class = PeopleForm
    template_name = 'contacts/edit_contact.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_type'] = 'person'
        return context

    def get_success_url(self):
        return reverse_lazy('contacts:person_detail', kwargs={'pk': self.object.pk})
@method_decorator(login_required, name='dispatch')    
class PersonDetailView(DetailView, LoginRequiredMixin):
    model = People
    template_name = 'contacts/person_detail.html'
    context_object_name = 'person'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person_content_type = ContentType.objects.get_for_model(People)
        context['recent_communications'] = ComLog.objects.filter(
            content_type=person_content_type,
            object_id=self.object.id
        ).order_by('-date_created')[:3]
        return context
    
logger = logging.getLogger(__name__)

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
    except Exception as e:
        logger.error(f"Error in contact search: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse(results, safe=False)

class SendEmailView(LoginRequiredMixin, FormView):
    template_name = 'contacts/send_email.html'
    form_class = EmailForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contact_type = self.kwargs['contact_type']
        contact_id = self.kwargs['contact_id']
        if contact_type == 'church':
            context['contact'] = get_object_or_404(Church, id=contact_id)
        else:  # person
            context['contact'] = get_object_or_404(People, id=contact_id)
        return context

    def form_valid(self, form):
        credentials_dict = self.request.session.get('google_credentials')
        if not credentials_dict:
            self.request.session['email_redirect_url'] = self.request.get_full_path()
            messages.info(self.request, 'Please connect your Google account to send emails.')
            return redirect(reverse('integrations:google_auth'))
        
        credentials = Credentials(**credentials_dict)
        try:
            service = build('gmail', 'v1', credentials=credentials)
            
            contact_type = self.kwargs['contact_type']
            contact_id = self.kwargs['contact_id']
            if contact_type == 'church':
                contact = get_object_or_404(Church, id=contact_id)
            else:  # person
                contact = get_object_or_404(People, id=contact_id)
            
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            
            # Add user's email signature if it exists
            if self.request.user.email_signature:
                body += f"\n\n{self.request.user.email_signature}"
            
            message = MIMEText(body)
            message['to'] = contact.email
            message['subject'] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            sent_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            
            # Create ComLog entry
            ComLog.objects.create(
                user=self.request.user,
                content_type=ContentType.objects.get_for_model(contact),
                object_id=contact.id,
                interaction_type='Email',
                communication_type='Email',
                subject=subject,
                notes=body,
                direction='Outgoing'
            )
            
            messages.success(self.request, 'Email sent successfully and logged.')
        except HttpError as error:
            messages.error(self.request, f'An error occurred: {error}')
        
        return super().form_valid(form)

    def get_success_url(self):
        contact_type = self.kwargs['contact_type']
        contact_id = self.kwargs['contact_id']
        if contact_type == 'church':
            return reverse('contacts:church_detail', kwargs={'pk': contact_id})
        else:
            return reverse('contacts:person_detail', kwargs={'pk': contact_id})