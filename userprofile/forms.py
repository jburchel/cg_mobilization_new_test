from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.exceptions import ValidationError


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_image', 'email_signature']
        widgets = {
            'profile_image': forms.FileInput(attrs={'accept': 'image/*'}),
            'email_signature': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True,
                             help_text="Please use your crossoverglobal.net email address.")
    profile_image = forms.ImageField(required=False)
    email_signature = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}),
                                      required=False,
                                      help_text="Enter your email signature. Line breaks will be preserved.")
    username = forms.EmailField(required=True,
                                help_text="Please use your crossoverglobal.net email address.")

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "profile_image", "email_signature")

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@crossoverglobal.net'):
            raise ValidationError("Please use your @crossoverglobal.net email address.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Set username to email
        if commit:
            user.save()
        return user
