from django import forms
from .models import Church, People

class PeopleForm(forms.ModelForm):
    class Meta:        
        model = People
        fields = ['first_name', 'last_name', 'email', 'phone', 'preferred_contact_method',
                  'street_address', 'city', 'state', 'zip_code', 'home_country',
                  'affiliated_church', 'marital_status', 'spouse_recruit', 'color', 'people_pipeline',
                  'priority', 'assigned_to', 'source', 'referred_by','image','initial_notes', 'info_given', 'desired_service',
                                  
                  ]
        
        widgets = {
            'initial_notes': forms.Textarea(attrs={'rows': 4}),
            'info_given': forms.Textarea(attrs={'rows': 4}),
            'desired_service': forms.Textarea(attrs={'rows': 4}),
        }

class ChurchForm(forms.ModelForm):    
    class Meta:
        model = Church
        fields = ['church_name', 'primary_contact_first_name', 'primary_contact_last_name', 'primary_contact_phone', 'primary_contact_email','preferred_contact_method',
                  'street_address', 'city', 'state', 'zip_code',
                  'senior_pastor_first_name','senior_pastor_last_name', 'senior_pastor_phone', 'senior_pastor_email',
                  'missions_pastor_first_name', 'missions_pastor_last_name','mission_pastor_phone', 'mission_pastor_email',
                  'virtuous', 'website', 'denomination','congregation_size', 
                  'color', 'church_pipeline', 'priority', 'assigned_to','source', 'referred_by', 'year_founded','initial_notes', 'info_given',
                  'image'
                  ]
        
        widgets = {
            'initial_notes': forms.Textarea(attrs={'rows': 4}),
            'info_given': forms.Textarea(attrs={'rows': 4}),
        }

# contacts/forms.py

from django import forms

class EmailForm(forms.Form):
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email subject'
        })
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter your message here'
        })
    )
    
        