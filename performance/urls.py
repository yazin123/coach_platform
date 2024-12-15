# performance/urls.py (Updated)
from django.urls import path
from . import views

urlpatterns = [
    path('log/', views.log_performance, name='log_performance'),
    path('history/', views.performance_history, name='performance_history'),
    path('goals/set/', views.set_goal, name='set_goal'),
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/<int:goal_id>/update/', views.update_goal_status, name='update_goal_status'),
]