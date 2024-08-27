import logging
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import ProfileImageForm, CustomUserCreationForm
import os


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after login
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'userprofile/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('userprofile:login')

logger = logging.getLogger(__name__)

@login_required
def account_view(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            if 'profile_image' in form.changed_data:
                logger.info(f"Profile image changed for user {user.username}")
                if 'profile_image' in request.FILES:
                    user.profile_image = request.FILES['profile_image']
                    logger.info(f"New profile image: {user.profile_image.name}")
                    logger.info(f"File size: {user.profile_image.size} bytes")
                    
                    # Check if the file was actually saved
                    expected_path = os.path.join(settings.MEDIA_ROOT, user.profile_image.name)
                    if os.path.exists(expected_path):
                        logger.info(f"File successfully saved at {expected_path}")
                    else:
                        logger.error(f"File not found at expected path: {expected_path}")
                    
                    # Log the MEDIA_ROOT and MEDIA_URL settings
                    logger.info(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
                    logger.info(f"MEDIA_URL: {settings.MEDIA_URL}")
                    
                    user.create_thumbnail()
                else:
                    user.profile_image = None
                    user.profile_thumbnail = None
                    logger.info("Profile image removed")
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('userprofile:account')
        else:
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        form = ProfileImageForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'userprofile/account.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')  # Redirect to home page after signup
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'userprofile/signup.html', {'form': form})

@login_required
def update_profile_image(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            user.create_thumbnail()
            messages.success(request, 'Profile image updated successfully.')
            return redirect('userprofile:account')
    else:
        form = ProfileImageForm(instance=request.user)
    return render(request, 'userprofile/update_profile_image.html', {'form': form})