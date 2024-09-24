"""
URL configuration for cg_mobilization project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home
import os

# Ensure MEDIA_ROOT exists
if settings.MEDIA_ROOT:
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('contacts/', include('contacts.urls')),
    path('accounts/', include('userprofile.urls')),
    path('com-log/', include('com_log.urls')),
    path('task-tracker/', include('task_tracker.urls')),
    path('integrations/', include('integrations.urls', namespace='integrations')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
else:
    # Serve media files using whitenoise in production
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
