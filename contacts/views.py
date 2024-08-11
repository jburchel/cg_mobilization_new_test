from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Contact, Church, People
from django.db.models import Count 
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

class ContactsListView(ListView):
    model = Contact
    template_name = 'contacts/contacts_list.html'
    context_object_name = 'contacts'
    paginate_by = 20  # Adjust this number as needed

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(church_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        queryset = queryset.select_related('church', 'people')
        
        for contact in queryset:
            if hasattr(contact, 'church'):
                contact.detail_url = 'contacts:church_detail'
                contact.contact_type = 'Church'
            elif hasattr(contact, 'people'):
                contact.detail_url = 'contacts:person_detail'
                contact.contact_type = 'Individual'
            else:
                contact.detail_url = 'contacts:contact_detail'
                contact.contact_type = 'Contact'
            
            contact.display_name = contact.get_name()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ChurchListView(ListView):
    model = Church
    template_name = 'contacts/church_list.html'
    context_object_name = 'churches'
    paginate_by = 20  # Adjust this number as needed

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(church_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(senior_pastor_last_name__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class PeopleListView(ListView):
    model = People
    template_name = 'contacts/people_list.html'
    context_object_name = 'people'
    ordering = ['last_name', 'first_name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all people
        people = self.get_queryset()

        # Calculate total number of people
        context['total_people'] = people.count()
        
        # Get pipeline stages and counts
        pipeline_summary = dict(people.values_list('people_pipeline').annotate(count=Count('people_pipeline')))
        
        # Create a dictionary to map database values to display values
        pipeline_choices = dict(People.PEOPLE_PIPELINE)

       # Convert keys to display values
        pipeline_summary = {pipeline_choices.get(key, key): value for key, value in pipeline_summary.items()}
        
        # Create pipeline stages dict with display values
        pipeline_stages_dict = {value: [] for value in pipeline_choices.values()}

        # Populate pipeline summary and stages
        for person in people:
            stage = person.get_people_pipeline_display()
            if stage in pipeline_stages_dict:
                pipeline_stages_dict[stage].append(person)

        context['pipeline_summary'] = pipeline_summary
        context['pipeline_stages'] = pipeline_stages_dict

        return context
    
    def get_queryset(self):
        # You can add any filtering or ordering here
        return super().get_queryset().select_related('contact_ptr')
        
class PersonDetailView(DetailView):
    model = People
    template_name = 'contacts/person_detail.html'
    context_object_name = 'person'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here if needed
        return context
    
class ChurchDetailView(DetailView):
    model = Church
    template_name = 'contacts/church_detail.html'
    context_object_name = 'church'

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
        person.people_pipeline = new_stage
        person.save()
        return JsonResponse({'success': True})
    except People.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Person not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
