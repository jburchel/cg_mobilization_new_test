from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.ContactListView.as_view(), name='contact_list'),
    path('church/<int:pk>/', views.ChurchDetailView.as_view(), name='church_detail'),
    path('person/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('church/<int:pk>/edit/', views.ChurchUpdateView.as_view(), name='church_edit'),
    path('person/<int:pk>/edit/', views.PersonUpdateView.as_view(), name='person_edit'),
    path('add/<str:contact_type>/', views.add_contact, name='add_contact'),
    path('<int:pk>/edit/', views.edit_contact, name='edit_contact'),
    path('people/', views.PeopleListView.as_view(), name='people_list'),
    path('update_pipeline_stage/', views.update_pipeline_stage, name='update_pipeline_stage'),
    path('churches/', views.ChurchListView.as_view(), name='church_list'),
    path('update_church_pipeline_stage/', views.update_church_pipeline_stage, name='update_church_pipeline_stage'),   
    path('api/search/', views.contact_search, name='contact_search'),  
    path('add/person/', views.PersonAddView.as_view(), name='add_person'),
    path('add/church/', views.ChurchAddView.as_view(), name='add_church'),
    path('<str:contact_type>/<int:contact_id>/send_email/', views.SendEmailView.as_view(), name='send_email'),
    path('get-church-pipeline-summary/', views.get_church_pipeline_summary, name='get_church_pipeline_summary'),
]