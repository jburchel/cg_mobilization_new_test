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
            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']
                logger.info(f"New profile image uploaded for user {user.username}: {user.profile_image.name}")
            user.save()
            logger.info(f"User saved. Profile image name: {user.profile_image.name if user.profile_image else 'No image'}")
            logger.info(f"User saved. Profile thumbnail name: {user.profile_thumbnail.name if user.profile_thumbnail else 'No thumbnail'}")
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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')  # or wherever you want to redirect after signup
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
