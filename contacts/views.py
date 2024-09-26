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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import logging
from django.utils.decorators import method_decorator
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from integrations.google_auth import credentials_to_dict, build_gmail_service
import base64
import os
import html
from django.conf import settings
from django.http import HttpResponseRedirect

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
                'last_contact': contact.date_modified.strftime('%Y-%m-%d') if contact.date_modified else '',
                'edit_url': reverse('contacts:edit_contact', kwargs={'pk': contact.id}),
                'detail_url': reverse('contacts:person_detail' if hasattr(contact, 'people') else 'contacts:church_detail', kwargs={'pk': contact.id}),
                'source': contact.source if hasattr(contact, 'source') else '',
                'title': contact.title if hasattr(contact, 'title') else '',
            }
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
class ChurchListView(ListView):
    model = Church
    template_name = 'contacts/church_list.html'
    context_object_name = 'churches'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Define all stages, even if they're empty
        all_stages = ['PROMOTION', 'INFORMATION', 'INVITATION', 'CONFIRMATION', 'EN42', 'AUTOMATION']
        
        # Get pipeline summary
        pipeline_summary = dict(Church.objects.values_list('church_pipeline').annotate(count=Count('church_pipeline')))
        
        # Get churches for each stage
        pipeline_stages = {stage: list(Church.objects.filter(church_pipeline=stage).values('id', 'church_name', 'email', 'date_modified')) for stage in all_stages}
        
        context.update({
            'all_stages': all_stages,
            'total_churches': Church.objects.count(),
            'pipeline_summary': pipeline_summary,
            'pipeline_stages': pipeline_stages,
        })
        
        # Add debug information
        context['debug_info'] = {
            'total_churches': context['total_churches'],
            'pipeline_summary': context['pipeline_summary'],
            'pipeline_stages_count': {stage: len(churches) for stage, churches in context['pipeline_stages'].items()},
        }
        
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
        return JsonResponse({'success': True, 'new_stage': new_stage_db_value})
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
        contact_content_type = ContentType.objects.get_for_model(Contact)
        
        recent_communications = ComLog.objects.filter(
            (Q(content_type=church_content_type) & Q(object_id=self.object.id)) |
            (Q(content_type=contact_content_type) & Q(object_id=self.object.contact_ptr_id))
        ).order_by('-date')
        
        logger.info(f"ChurchDetailView: Fetched {recent_communications.count()} recent communications for Church {self.object.id}")
        for comm in recent_communications:
            logger.info(f"ChurchDetailView: ComLog: {comm.id}, Date: {comm.date}, Type: {comm.communication_type}, Content Type: {comm.content_type}")
        
        context['recent_communications'] = recent_communications
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
        if 'image' in self.request.FILES:
            form.instance.image = self.request.FILES['image']
        response = super().form_valid(form)
        messages.success(self.request, f'Church "{self.object.church_name}" has been updated successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_type'] = 'church'
        return context

    def get_success_url(self):
        return reverse_lazy('contacts:contact_list')
    
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
        new_stage_db_value = next((key for key, value in People.PEOPLE_PIPELINE if value.lower().replace(' ', '-') == new_stage.lower()), None)
        
        if new_stage_db_value is None:
            return JsonResponse({'success': False, 'error': f'Invalid stage: {new_stage}'}, status=400)
        
        person.people_pipeline = new_stage_db_value
        person.save()

        # Calculate updated summary
        pipeline_choices = dict(People.PEOPLE_PIPELINE)
        pipeline_summary = {stage: People.objects.filter(people_pipeline=key).count() for key, stage in pipeline_choices.items()}
        total_people = People.objects.count()

        # Convert to list and sort by the order in PEOPLE_PIPELINE
        sorted_summary = sorted(
            pipeline_summary.items(),
            key=lambda x: list(pipeline_choices.values()).index(x[0])
        )

        # Add total to the beginning of the summary
        sorted_summary.insert(0, ('Total', total_people))

        return JsonResponse({
            'success': True,
            'new_stage': new_stage_db_value,
            'summary': sorted_summary
        })
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
        if 'image' in self.request.FILES:
            form.instance.image = self.request.FILES['image']
        response = super().form_valid(form)        
        messages.success(self.request, f'Person "{self.object.get_name()}" has been updated successfully.')
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
        contact_content_type = ContentType.objects.get_for_model(Contact)
        
        recent_communications = ComLog.objects.filter(
            (Q(content_type=person_content_type) & Q(object_id=self.object.id)) |
            (Q(content_type=contact_content_type) & Q(object_id=self.object.contact_ptr_id))
        ).order_by('-date')
        
        logger.info(f"PersonDetailView: Fetched {recent_communications.count()} recent communications for Person {self.object.id}")
        for comm in recent_communications:
            logger.info(f"PersonDetailView: ComLog: {comm.id}, Date: {comm.date}, Type: {comm.communication_type}, Content Type: {comm.content_type}")
        
        context['recent_communications'] = recent_communications
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
            contact = get_object_or_404(Church, id=contact_id)
            context['contact_name'] = contact.church_name            
        else:  # person
            contact = get_object_or_404(People, id=contact_id)
            context['contact_name'] = f"{contact.first_name} {contact.last_name}"                        

        context['contact_email'] = contact.email
        return context

    def form_valid(self, form):
        try:
            credentials_dict = self.request.session.get('google_credentials')
            if not credentials_dict:
                self.request.session['email_redirect_url'] = self.request.get_full_path()
                return HttpResponseRedirect(reverse('integrations:google_auth'))

            credentials = Credentials(
                token=credentials_dict['token'],
                refresh_token=credentials_dict['refresh_token'],
                token_uri=credentials_dict['token_uri'],
                client_id=credentials_dict['client_id'],
                client_secret=credentials_dict['client_secret'],
                scopes=credentials_dict['scopes']
            )

            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                self.request.session['google_credentials'] = credentials_to_dict(credentials)

            service = build_gmail_service(credentials)

            contact_type = self.kwargs['contact_type']
            contact_id = self.kwargs['contact_id']
            if contact_type == 'church':
                contact = get_object_or_404(Church, id=contact_id)
            else:  # person
                contact = get_object_or_404(People, id=contact_id)
            
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            
            message = MIMEMultipart('related')
            message['to'] = contact.email
            message['subject'] = subject

            # Convert line breaks to HTML paragraphs
            body_html = ''.join(f'<p>{html.escape(paragraph)}</p>' for paragraph in body.split('\n\n'))
            # Convert single line breaks to <br> tags
            body_html = body_html.replace('\n', '<br>')

            logo_cid = "company_logo"
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                {body_html}
                {self.request.user.email_signature or ''}
                <img src="cid:{logo_cid}" alt="Company Logo" style="max-width: 300px; margin-top: 10px;">
            </body>
            </html>
            """
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
             # Attach the logo
            logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'company_logo.png')
            with open(logo_path, 'rb') as img:
                img_data = img.read()
            logo_part = MIMEImage(img_data, name='company_logo.png')
            logo_part.add_header('Content-ID', f'<{logo_cid}>')
            logo_part.add_header('Content-Disposition', 'inline')
            message.attach(logo_part)

            # Plain text version
            text_content = f"{body}\n\n{self.request.user.email_signature or ''}"
            text_part = MIMEText(text_content, 'plain')
            message.attach(text_part)  

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            try:
                sent_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
                logger.info(f"Email sent successfully. Message ID: {sent_message['id']}")

                # Create ComLog entry
                ComLog.objects.create(
                    user=self.request.user,
                    content_type=ContentType.objects.get_for_model(Contact),
                    object_id=contact.id,
                    interaction_type='Email',
                    communication_type='Email',
                    subject=subject,
                    notes=body,
                    direction='Outgoing'
                )

                messages.success(self.request, "Email sent successfully and logged.")
            except Exception as e:
                logger.error(f"Error sending email: {str(e)}")
                raise

            return HttpResponseRedirect(reverse('task_tracker:task_create'))

        except Exception as e:
            logger.exception("Error in SendEmailView.form_valid")
            messages.error(self.request, f"Error sending email: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your form. Please check and try again.")
        return super().form_invalid(form)

    def get_success_url(self):
        contact_type = self.kwargs['contact_type']
        contact_id = self.kwargs['contact_id']
        if contact_type == 'church':
            return reverse('contacts:church_detail', kwargs={'pk': contact_id})
        else:  # person
            return reverse('contacts:person_detail', kwargs={'pk': contact_id})
        
def get_church_pipeline_summary(request):
    pipeline_summary = dict(Church.objects.values_list('church_pipeline').annotate(count=Count('church_pipeline')))
    total_churches = Church.objects.count()
    
    return JsonResponse({
        'total_churches': total_churches,
        'pipeline_summary': pipeline_summary
    })