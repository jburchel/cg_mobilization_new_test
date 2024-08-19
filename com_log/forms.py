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

    class Meta:
        model = ComLog
        fields = ['contact_type', 'contact', 'communication_type', 'summary']

    def clean(self):
        cleaned_data = super().clean()
        contact_type = cleaned_data.get('contact_type')
        contact_name = cleaned_data.get('contact')

        logger.info(f"Cleaning form data: contact_type={contact_type}, contact_name={contact_name}")

        if contact_type == 'church':
            try:
                contact = Church.objects.get(church_name=contact_name)
                logger.info(f"Found church: {contact}")
            except Church.DoesNotExist:
                logger.error(f"Church not found: {contact_name}")
                self.add_error('contact', 'Selected church does not exist.')
        elif contact_type == 'people':
            try:
                last_name, first_name = contact_name.rsplit(' ', 1)
                contact = People.objects.get(last_name=last_name, first_name=first_name)
                logger.info(f"Found person: {contact}")
            except (ValueError, People.DoesNotExist):
                logger.error(f"Person not found: {contact_name}")
                self.add_error('contact', 'Selected person does not exist.')
        else:
            logger.error(f"Invalid contact type: {contact_type}")
            self.add_error('contact_type', 'Invalid contact type.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        contact_type = self.cleaned_data['contact_type']
        contact_name = self.cleaned_data['contact']

        logger.info(f"Saving ComLog: contact_type={contact_type}, contact_name={contact_name}")

        try:
            if contact_type == 'church':
                contact = Church.objects.get(church_name=contact_name)
            else:
                last_name, first_name = contact_name.rsplit(' ', 1)
                contact = People.objects.get(last_name=last_name, first_name=first_name)

            instance.content_type = ContentType.objects.get_for_model(type(contact))
            instance.object_id = contact.id

            if commit:
                instance.save()
                logger.info(f"ComLog saved: {instance.id}")
            return instance
        except Exception as e:
            logger.error(f"Error saving ComLog: {str(e)}")
            raise