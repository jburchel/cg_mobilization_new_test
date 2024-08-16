from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from contacts.models import Church, People  # Add this import

class CommunicationLog(models.Model):
    COMMUNICATION_TYPES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('text', 'Text'),
        ('meeting', 'Meeting'),
        ('video', 'Video Conference'),
        ('facebook', 'Facebook Messenger'),
        ('whatsapp', 'WhatsApp'),
        ('signal', 'Signal'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    contact = GenericForeignKey('content_type', 'object_id')

    date = models.DateTimeField(auto_now_add=True)
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    summary = models.TextField()

    class Meta:
        ordering = ['-date']  # Add this to address the pagination warning

    def __str__(self):
        return f"{self.get_communication_type_display()} on {self.date}"

    def get_contact_name(self):
        if self.contact:
            if isinstance(self.contact, Church):
                return self.contact.church_name
            elif isinstance(self.contact, People):
                return f"{self.contact.first_name} {self.contact.last_name}".strip()
        return "No Contact"

    def get_contact_type(self):
        if self.contact:
            if hasattr(self.contact, 'church_name'):
                return 'Church'
            elif hasattr(self.contact, 'first_name') and hasattr(self.contact, 'last_name'):
                return 'Person'
            else:
                return f"Unknown"
        return "No Contact"

    def get_debug_info(self):
        info = {
            'content_type': self.content_type.model,
            'object_id': self.object_id,
            'contact_attributes': [],
            'contact_class': self.contact.__class__.__name__ if self.contact else 'None',
            'detected_type': self.get_contact_type(),
            'mismatch': False
        }
        if self.contact:
            for field in self.contact._meta.fields:
                if not field.name.startswith('_'):
                    value = getattr(self.contact, field.name, 'N/A')
                    if not callable(value):
                        info['contact_attributes'].append(f"{field.name}: {value}")
            
            # Check for mismatch
            if (info['content_type'] == 'people' and info['detected_type'] == 'Church') or \
               (info['content_type'] == 'church' and info['detected_type'] == 'Person'):
                info['mismatch'] = True

        return info