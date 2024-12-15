# training/forms.py
from django import forms
from users.models import TrainingSession
from users.models import Athlete

class TrainingSessionForm(forms.ModelForm):
    athlete = forms.ModelChoiceField(
        queryset=Athlete.objects.all(),
        label='Select Athlete'
    )

    class Meta:
        model = TrainingSession
        fields = ['athlete', 'session_date', 'session_type', 'description', 'status']
        widgets = {
            'session_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }