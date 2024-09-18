from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ComLog(models.Model):
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    contact = GenericForeignKey('content_type', 'object_id')
    interaction_type = models.CharField(max_length=20)
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    subject = models.CharField(max_length=255, blank=True)
    notes = models.TextField()
    direction = models.CharField(max_length=10, choices=[('Incoming', 'Incoming'), ('Outgoing', 'Outgoing')],default='Outgoing')
    date = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Communication with {self.contact} on {self.date}"

    def get_contact_name(self):
        return str(self.contact) if self.contact else "No Contact"

    def get_contact_type(self):
        return self.content_type.model.capitalize() if self.content_type else "Unknown"