from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_image']
        widgets = {
            'profile_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "profile_image")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user