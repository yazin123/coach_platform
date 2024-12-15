# performance/forms.py
from django import forms
from users.models import PerformanceLog, Goal

class PerformanceLogForm(forms.ModelForm):
    class Meta:
        model = PerformanceLog
        fields = ['activity_type', 'duration', 'intensity_level', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['goal_type', 'description', 'target_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }