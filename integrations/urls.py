from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    path('google/auth/', views.google_auth, name='google_auth'),
    path('google/auth/callback/', views.google_auth_callback, name='google_auth_callback'),
    path('settings/', views.settings_view, name='settings'),
    path('test/', views.test_integration, name='test_integration'),
    path('revoke/', views.revoke_access, name='revoke_access'),
]