from django import forms
from users.models import Injury
from .models import TreatmentNote

class InjuryForm(forms.ModelForm):
    """Form for creating a new injury record."""
    
    other_injury_type = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specify the injury type'})
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Initial assessment notes...'}),
        required=False
    )
    
    class Meta:
        model = Injury
        fields = ['athlete', 'injury_type', 'injury_date', 'expected_recovery_date', 'description', 'status']
        widgets = {
            'athlete': forms.Select(attrs={'class': 'form-select'}),
            'injury_type': forms.Select(attrs={'class': 'form-select'}),
            'injury_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_recovery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['injury_type'].choices = [
            ('', 'Select injury type'),
            ('Sprain', 'Sprain'),
            ('Strain', 'Strain'),
            ('Fracture', 'Fracture'),
            ('Dislocation', 'Dislocation'),
            ('Contusion', 'Contusion'),
            ('Laceration', 'Laceration'),
            ('Tendonitis', 'Tendonitis'),
            ('Bursitis', 'Bursitis'),
            ('Concussion', 'Concussion'),
            ('Other', 'Other'),
        ]

class InjuryUpdateForm(forms.ModelForm):
    """Form for updating an existing injury record."""
    
    other_injury_type = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specify the injury type'})
    )
    
    update_notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes about this update...'}),
        required=False
    )
    
    recovery_progress = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'type': 'range', 'step': '5'})
    )
    
    class Meta:
        model = Injury
        fields = ['injury_type', 'injury_date', 'expected_recovery_date', 'description', 'status']
        widgets = {
            'injury_type': forms.Select(attrs={'class': 'form-select'}),
            'injury_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_recovery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['injury_type'].choices = [
            ('', 'Select injury type'),
            ('Sprain', 'Sprain'),
            ('Strain', 'Strain'),
            ('Fracture', 'Fracture'),
            ('Dislocation', 'Dislocation'),
            ('Contusion', 'Contusion'),
            ('Laceration', 'Laceration'),
            ('Tendonitis', 'Tendonitis'),
            ('Bursitis', 'Bursitis'),
            ('Concussion', 'Concussion'),
            ('Other', 'Other'),
        ]

class TreatmentNoteForm(forms.ModelForm):
    """Form for adding a treatment note to an injury."""
    
    class Meta:
        model = TreatmentNote
        fields = ['title', 'date', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }