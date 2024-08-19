from django.db import models
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

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    contact = GenericForeignKey('content_type', 'object_id')

    date = models.DateTimeField(auto_now_add=True)
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    summary = models.TextField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_communication_type_display()} on {self.date}"

    def get_contact_name(self):
        return str(self.contact) if self.contact else "No Contact"

    def get_contact_type(self):
        return self.content_type.model.capitalize() if self.content_type else "Unknown"