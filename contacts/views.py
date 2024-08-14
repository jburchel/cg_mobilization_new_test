from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import PeopleForm, ChurchForm
from django.views.generic import ListView, DetailView, UpdateView
from django.db.models import Q
from .models import Contact, Church, People
from django.db.models import Count 
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers.json import DjangoJSONEncoder
import logging

logger = logging.getLogger(__name__)

class ContactListView(ListView):
    model = Contact
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        return Contact.objects.select_related('church', 'people').order_by('last_name', 'first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contacts_data = []
        for contact in context['contacts']:
            contact_type = 'Church' if hasattr(contact, 'church') else 'Person'
            contacts_data.append({
                'id': contact.id,
                'name': contact.get_name(),
                'type': contact_type,
                'email': contact.email,
                'phone': contact.phone,
                'last_contact': contact.date_modified.strftime('%Y-%m-%d') if contact.date_modified else ''
            })
        context['contacts_json'] = json.dumps(contacts_data, cls=DjangoJSONEncoder)
        return context
    
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

class ChurchListView(ListView):
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
    
class ChurchDetailView(DetailView):
    model = Church
    template_name = 'contacts/church_detail.html'
    context_object_name = 'church'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here if needed
        return context
    
class ChurchUpdateView(UpdateView):
    model = Church
    form_class = ChurchForm
    template_name = 'contacts/edit_contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_type'] = 'church'
        return context

    def get_success_url(self):
        return reverse_lazy('contacts:contact_list')

class PeopleListView(ListView):
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
        
class PersonDetailView(DetailView):
    model = People
    template_name = 'contacts/person_detail.html'
    context_object_name = 'person'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here if needed
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
    
class PersonUpdateView(UpdateView):
    model = People
    form_class = PeopleForm
    template_name = 'contacts/edit_contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_type'] = 'person'
        return context

    def get_success_url(self):
        return reverse_lazy('contacts:contact_list')
    

