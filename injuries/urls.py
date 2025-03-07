from django.urls import path
from . import views

urlpatterns = [
    path('', views.injury_list, name='injury_list'),
    path('add/', views.add_injury, name='add_injury'),
    path('<int:injury_id>/', views.injury_detail, name='injury_detail'),
    path('<int:injury_id>/update/', views.update_injury, name='update_injury'),
    path('<int:injury_id>/resolve/', views.mark_injury_resolved, name='mark_injury_resolved'),
    path('<int:injury_id>/add-note/', views.add_treatment_note, name='add_treatment_note'),
    path('<int:injury_id>/update-status/', views.update_injury_status, name='update_injury_status'),
]