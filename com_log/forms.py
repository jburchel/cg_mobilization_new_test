from django import forms
from .models import ComLog
from contacts.models import Church, People
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

class ComLogForm(forms.ModelForm):
    CONTACT_TYPE_CHOICES = [('church', 'Church'), ('people', 'Person')]
    
    contact_type = forms.ChoiceField(choices=CONTACT_TYPE_CHOICES)
    contact = forms.CharField(widget=forms.TextInput(attrs={'class': 'contact-search', 'placeholder': 'Search for a contact...'}))
    contact_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = ComLog
        fields = ['contact_type', 'contact', 'contact_id', 'communication_type', 'notes']

    def clean(self):
        cleaned_data = super().clean()
        contact_type = cleaned_data.get('contact_type')
        contact_name = cleaned_data.get('contact')
        contact_id = cleaned_data.get('contact_id')

        logger.info(f"Cleaning form data: contact_type={contact_type}, contact_name={contact_name}, contact_id={contact_id}")

        if contact_type == 'church':
            try:
                contact = Church.objects.get(id=contact_id)
                logger.info(f"Found church: {contact}")
            except Church.DoesNotExist:
                logger.error(f"Church not found: id={contact_id}, name={contact_name}")
                self.add_error('contact', 'Selected church does not exist.')
        elif contact_type == 'people':
            try:
                contact = People.objects.get(id=contact_id)
                logger.info(f"Found person: {contact}")
            except People.DoesNotExist:
                logger.error(f"Person not found: id={contact_id}, name={contact_name}")
                self.add_error('contact', 'Selected person does not exist.')
        else:
            logger.error(f"Invalid contact type: {contact_type}")
            self.add_error('contact_type', 'Invalid contact type.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        contact_type = self.cleaned_data['contact_type']
        contact_id = self.cleaned_data['contact_id']

        logger.info(f"Saving ComLog: contact_type={contact_type}, contact_id={contact_id}")

        try:
            if contact_type == 'church':
                contact = Church.objects.get(id=contact_id)
            else:
                contact = People.objects.get(id=contact_id)

            instance.content_type = ContentType.objects.get_for_model(type(contact))
            instance.object_id = contact.id

            if commit:
                instance.save()
                logger.info(f"ComLog saved: {instance.id}")
            return instance
        except Exception as e:
            logger.error(f"Error saving ComLog: {str(e)}")
            raise