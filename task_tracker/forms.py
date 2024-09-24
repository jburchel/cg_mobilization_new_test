from django import forms
from .models import Task
from contacts.models import Contact
from django.utils import timezone
from django.forms.widgets import DateTimeInput

class TaskForm(forms.ModelForm):
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Associated Contact",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    due_date = forms.DateTimeField(
        widget=DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'],
        initial=timezone.now
    )

    reminder = forms.ChoiceField(
        choices=Task.REMINDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    custom_reminder = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        help_text="Enter custom reminder time in minutes"
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'assigned_to', 'due_date', 'contact', 'reminder', 'custom_reminder']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        reminder = cleaned_data.get("reminder")
        custom_reminder = cleaned_data.get("custom_reminder")

        if reminder == 'custom' and not custom_reminder:
            raise forms.ValidationError("Please provide a custom reminder time.")

        return cleaned_data