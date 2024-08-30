# integrations/urls.py

from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    path('google/auth/', views.google_auth, name='google_auth'),
    path('google/auth/callback/', views.google_auth_callback, name='google_auth_callback'),
    path('google/auth/success/', views.GoogleAuthSuccessView.as_view(), name='google_auth_success'),
]