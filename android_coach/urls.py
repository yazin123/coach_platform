# android_coach/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('training/', include('training.urls')),
    path('performance/', include('performance.urls')),
     path('injuries/', include('injuries.urls')), 
]