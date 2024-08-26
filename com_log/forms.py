from django import forms
from .models import ComLog
from contacts.models import Church, People, Contact
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

class ComLogForm(forms.ModelForm):
    CONTACT_TYPES = [
        ('church', 'Church'),
        ('person', 'Person'),
    ]

    contact_type = forms.ChoiceField(choices=CONTACT_TYPES, widget=forms.Select(attrs={'class': 'form-control'}))
    contact = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    contact_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = ComLog
        fields = ['contact_type', 'contact', 'contact_id', 'communication_type', 'notes']
        widgets = {
            'communication_type': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        contact_type = cleaned_data.get('contact_type')
        contact_id = cleaned_data.get('contact_id')

        if contact_type == 'church':
            content_type = ContentType.objects.get_for_model(Church)
        elif contact_type == 'person':
            content_type = ContentType.objects.get_for_model(People)
        else:
            raise forms.ValidationError("Invalid contact type")

        cleaned_data['content_type'] = content_type
        cleaned_data['object_id'] = contact_id

        return cleaned_data