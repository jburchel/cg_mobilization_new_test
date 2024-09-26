from django import forms
from .models import ComLog
from contacts.models import Contact, Church, People
from django.contrib.contenttypes.models import ContentType

class ComLogForm(forms.ModelForm):
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        label="Contact",
        empty_label="Select a contact"
    )

    class Meta:
        model = ComLog
        fields = ['contact', 'communication_type', 'notes']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = Contact.objects.all().order_by('church_name', 'last_name', 'first_name')
        self.fields['contact'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        if hasattr(obj, 'church'):
            return f"{obj.church_name} (Church)"
        elif hasattr(obj, 'people'):
            return f"{obj.first_name} {obj.last_name} (Person)"
        else:
            return f"{obj.email} (Contact)"

    def save(self, commit=True):
        instance = super().save(commit=False)
        contact = self.cleaned_data['contact']
        
        # Determine the correct content type
        if hasattr(contact, 'church'):
            content_type = ContentType.objects.get_for_model(Church)
            object_id = contact.church.id
        elif hasattr(contact, 'people'):
            content_type = ContentType.objects.get_for_model(People)
            object_id = contact.people.id
        else:
            content_type = ContentType.objects.get_for_model(Contact)
            object_id = contact.id

        instance.content_type = content_type
        instance.object_id = object_id
        instance.user = self.user

        if commit:
            instance.save()
        return instance