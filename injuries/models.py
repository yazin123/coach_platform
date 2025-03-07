from django.db import models
from django.conf import settings
from users.models import Injury

class TreatmentNote(models.Model):
    """Model for storing treatment notes related to injuries."""
    
    injury = models.ForeignKey(Injury, on_delete=models.CASCADE, related_name='treatment_notes')
    title = models.CharField(max_length=100)
    date = models.DateField()
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.date})"
    
    class Meta:
        ordering = ['-date', '-created_at']