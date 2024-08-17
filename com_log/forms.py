from django import forms
from .models import ComLog
from contacts.models import Contact, People, Church
from django.contrib.contenttypes.models import ContentType

class ComLogForm(forms.ModelForm):    
    CONTACT_TYPE_CHOICES = [('church', 'Church'), ('people', 'Person')]
    
    contact_type = forms.ChoiceField(choices=CONTACT_TYPE_CHOICES)
    contact = forms.CharField(widget=forms.TextInput(attrs={'class': 'contact-search', 'placeholder': 'Search for a contact...'}))

    class Meta:
        model = ComLog
        fields = ['contact_type', 'contact', 'communication_type', 'summary']        
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            content_type = self.instance.content_type
            if content_type:
                if content_type.model == 'church':
                    self.initial['contact_type'] = 'church'
                    church = Church.objects.filter(id=self.instance.object_id).first()
                    if church:
                        self.initial['contact'] = church.church_name
                elif content_type.model == 'people':
                    self.initial['contact_type'] = 'people'
                    person = People.objects.filter(id=self.instance.object_id).first()
                    if person:
                        self.initial['contact'] = f"{person.first_name} {person.last_name}"
            if not self.initial.get('contact'):
                self.initial['contact'] = 'Contact not found'

    def clean(self):
        cleaned_data = super().clean()
        contact_type = cleaned_data.get('contact_type')
        contact_name = cleaned_data.get('contact')

        if contact_type == 'church':
            try:
                contact = Church.objects.get(church_name=contact_name)
            except Church.DoesNotExist:
                self.add_error('contact', 'Selected church does not exist.')
        elif contact_type == 'people':
            try:
                last_name, first_name = contact_name.rsplit(' ', 1)
                contact = People.objects.get(last_name=last_name, first_name=first_name)
            except (ValueError, People.DoesNotExist):
                self.add_error('contact', 'Selected person does not exist.')
        else:
            self.add_error('contact_type', 'Invalid contact type.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        contact_type = self.cleaned_data['contact_type']
        contact_name = self.cleaned_data['contact']

        if contact_type == 'church':
            contact = Church.objects.get(church_name=contact_name)
        else:
            last_name, first_name = contact_name.rsplit(' ', 1)
            contact = People.objects.get(last_name=last_name, first_name=first_name)

        instance.content_type = ContentType.objects.get_for_model(type(contact))
        instance.object_id = contact.id
        
        if commit:
            instance.save()
        return instance