from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.ContactsListView.as_view(), name='all_contacts'),
    path('churches/', views.ChurchListView.as_view(), name='church_list'),
    path('people/', views.PeopleListView.as_view(), name='people_list'),
    path('person/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('people/', views.ChurchListView.as_view(), name='church_list'),
    path('church/<int:pk>/', views.ChurchDetailView.as_view(), name='church_detail'),
    path('update_pipeline_stage/', views.update_pipeline_stage, name='update_pipeline_stage'),
]