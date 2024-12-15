# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Athlete, Coach, Physiotherapist, Admin

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('athlete', 'Athlete'),
        ('coach', 'Coach'),
        ('physio', 'Physiotherapist')
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

class AthleteProfileForm(forms.ModelForm):
    class Meta:
        model = Athlete
        fields = ['full_name', 'birth_date', 'sport', 'gender']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        # Add any specific validation for birth date if needed
        return birth_date

class CoachProfileForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = ['full_name', 'specialization']

class PhysiotherapistProfileForm(forms.ModelForm):
    class Meta:
        model = Physiotherapist
        fields = ['full_name', 'specialty']

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['full_name']