from django import forms
from .models import CommunicationLog
from contacts.models import Contact, People, Church
from django.contrib.contenttypes.models import ContentType

class CommunicationLogForm(forms.ModelForm):    
    contact_type = forms.ChoiceField(choices=[('church', 'Church'), ('people', 'Person')])
    contact = forms.ModelChoiceField(queryset=Church.objects.all())

    class Meta:
        model = CommunicationLog
        fields = ['contact_type', 'contact', 'communication_type', 'summary']        
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Church.objects.all() if self.initial.get('contact_type') == 'church' else People.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        contact_type = cleaned_data.get('contact_type')
        contact = cleaned_data.get('contact')

        if contact_type == 'church' and not isinstance(contact, Church):
            self.add_error('contact', 'Please select a church.')
        elif contact_type == 'people' and not isinstance(contact, People):
            self.add_error('contact', 'Please select a person.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        contact = self.cleaned_data['contact']
        instance.content_type = ContentType.objects.get_for_model(type(contact))
        instance.object_id = contact.id
        if commit:
            instance.save()
        return instance
    
