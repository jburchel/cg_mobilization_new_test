from django import forms
from .models import ComLog
from contacts.models import Church, People, Contact
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

class ComLogForm(forms.ModelForm):
    CONTACT_TYPE_CHOICES = [
        ('person', 'Person'),
        ('church', 'Church'),
    ]
    
    contact_type = forms.ChoiceField(choices=CONTACT_TYPE_CHOICES)
    contact = forms.CharField(max_length=100)  # This will be populated by JavaScript
    contact_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = ComLog
        fields = ['contact_type', 'contact', 'contact_id', 'communication_type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if isinstance(self.instance.contact, People):
                self.initial['contact_type'] = 'person'
                self.initial['contact'] = self.instance.contact.first_name + self.instance.contact.last_name
            elif isinstance(self.instance.contact, Church):
                self.initial['contact_type'] = 'church'
                self.initial['contact'] = self.instance.contact.church_name
            self.initial['contact_id'] = self.instance.contact.id

    def clean(self):
        cleaned_data = super().clean()
        contact_type = cleaned_data.get('contact_type')
        contact_id = cleaned_data.get('contact_id')

        if contact_type == 'person':
            try:
                contact = Contact.objects.get(id=contact_id)
            except Contact.DoesNotExist:
                raise forms.ValidationError("Selected person does not exist.")
        elif contact_type == 'church':
            try:
                contact = Church.objects.get(id=contact_id)
            except Church.DoesNotExist:
                raise forms.ValidationError("Selected church does not exist.")
        else:
            raise forms.ValidationError("Invalid contact type.")

        cleaned_data['contact'] = contact
        return cleaned_data