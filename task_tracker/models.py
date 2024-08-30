from django.db import models
from django.contrib.auth import get_user_model
from contacts.models import Contact
from django.utils import timezone

User = get_user_model()

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    REMINDER_CHOICES = [
        ('15_min', '15 minutes before'),
        ('30_min', '30 minutes before'),
        ('1_hour', '1 hour before'),
        ('2_hours', '2 hours before'),
        ('1_day', '1 day before'),
        ('1_week', '1 week before'),
        ('custom', 'Custom'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    google_calendar_event_id = models.CharField(max_length=255, blank=True, null=True)
    reminder = models.CharField(max_length=20, choices=REMINDER_CHOICES, default='30_min')
    custom_reminder = models.IntegerField(null=True, blank=True, help_text="Custom reminder time in minutes")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']