from django.urls import path
from . import views

app_name = 'com_log'

urlpatterns = [
    path('', views.ComLogListView.as_view(), name='list'),
    path('<int:pk>/', views.ComLogDetailView.as_view(), name='detail'),
    path('new/', views.ComLogCreateView.as_view(), name='create'),
    #path('<int:pk>/view/', views.view_com_log, name='view_com_log'),
    path('<int:pk>/edit/', views.ComLogUpdateView.as_view(), name='update'),
    # path('<int:pk>/delete/', views.delete_com_log, name='delete_com_log'),
    path('api/contacts/search/', views.contact_search, name='contact_search'),
    path('contact/<str:contact_type>/<int:contact_id>/', views.ContactInteractionsListView.as_view(), name='contact_interactions'),
]