from django.urls import path
from . import views
from .views import TaskDetailView

app_name = 'task_tracker'
    
urlpatterns = [
    path('', views.TaskListView.as_view(), name='task_list'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('create/<int:com_log_id>/', views.TaskCreateView.as_view(), name='task_create_from_com_log'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('<int:pk>/update-status/', views.update_task_status, name='update_task_status'),    
]