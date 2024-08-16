from django.urls import path
from . import views

app_name = 'com_log'

urlpatterns = [
    path('', views.CommunicationLogListView.as_view(), name='com_log_list'),
    path('<int:pk>/', views.CommunicationLogDetailView.as_view(), name='com_log_detail'),
    path('add/', views.AddComLogView.as_view(), name='add_com_log'),
    #path('<int:pk>/view/', views.view_com_log, name='view_com_log'),
    path('<int:pk>/edit/', views.EditComLogView.as_view(), name='edit_com_log'),
    # path('<int:pk>/delete/', views.delete_com_log, name='delete_com_log'),
]