from django.urls import path
from . import views

app_name = 'com_log'

urlpatterns = [
    path('', views.ComLogListView.as_view(), name='list'),
    path('<int:pk>/', views.ComLogDetailView.as_view(), name='detail'),
    path('new/', views.ComLogCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ComLogUpdateView.as_view(), name='update'),
    path('api/contacts/search/', views.contact_search, name='contact_search'),
    path('interactions/<str:contact_type>/<int:contact_id>/', views.ContactInteractionsListView.as_view(), name='contact_interactions'),
    path('contact-search/', views.contact_search, name='contact_search'),
    path('api/create/', views.create_com_log_entry, name='api_create'),  # New URL pattern for create_com_log_entry
]