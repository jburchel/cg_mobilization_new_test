from django.urls import path
from . import views
from .views import TaskDetailView

app_name = 'task_tracker'
    
urlpatterns = [
    path('', views.TaskListView.as_view(), name='task_list'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('<int:pk>/update-status/', views.update_task_status, name='update_task_status'),
    path('<int:pk>/update-status/', views.update_task_status, name='update_task_status'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('google-auth/', views.google_auth, name='google_auth'),
    path('google-auth-callback/', views.google_auth_callback, name='google_auth_callback'),
    path('initiate-google-auth/', views.initiate_google_auth, name='initiate_google_auth'),
]