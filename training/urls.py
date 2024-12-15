# training/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_training_session, name='create_training_session'),
    path('list/', views.training_session_list, name='training_session_list'),
    path('detail/<int:session_id>/', views.training_session_detail, name='training_session_detail'),
]