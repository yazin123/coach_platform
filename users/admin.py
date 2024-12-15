# In users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Athlete, Coach, Physiotherapist, Admin


admin.site.register(User)
admin.site.register(Athlete)
admin.site.register(Coach)
admin.site.register(Physiotherapist)
admin.site.register(Admin)