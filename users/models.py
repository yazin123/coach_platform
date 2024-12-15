from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('athlete', 'Athlete'),
        ('coach', 'Coach'),
        ('physio', 'Physiotherapist')
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def get_profile(self):
        """
        Retrieve the user's profile based on their role
        """
        try:
            if self.role == 'athlete':
                return self.athlete
            elif self.role == 'coach':
                return self.coach
            elif self.role == 'physio':
                return self.physiotherapist
            elif self.role == 'admin':
                return self.admin
        except ObjectDoesNotExist:
            return None

    def has_complete_profile(self):
        """
        Check if the user has a complete profile
        """
        profile = self.get_profile()
        return profile is not None

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name

class Athlete(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    sport = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __str__(self):
        return self.full_name

class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name

class Physiotherapist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name

class TrainingSession(models.Model):
    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed')
    )
    coach = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    session_date = models.DateTimeField()
    session_type = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    def __str__(self):
        return f"{self.athlete.full_name} - {self.session_type} on {self.session_date}"

class Injury(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('recovering', 'Recovering'),
        ('resolved', 'Resolved')
    )
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    physiotherapist = models.ForeignKey(Physiotherapist, on_delete=models.SET_NULL, null=True)
    injury_type = models.CharField(max_length=100)
    injury_date = models.DateField()
    expected_recovery_date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.athlete.full_name} - {self.injury_type}"

class PerformanceLog(models.Model):
    INTENSITY_CHOICES = [(i, str(i)) for i in range(1, 11)]
    
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    log_date = models.DateTimeField(auto_now_add=True)
    activity_type = models.CharField(max_length=50)
    duration = models.FloatField(validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True, null=True)
    intensity_level = models.IntegerField(
        choices=INTENSITY_CHOICES, 
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    def __str__(self):
        return f"{self.athlete.full_name} - {self.activity_type} on {self.log_date}"

class Goal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('achieved', 'Achieved'),
        ('abandoned', 'Abandoned')
    )
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=50)
    description = models.TextField()
    target_date = models.DateField()
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('achieved', 'Achieved'),
        ('abandoned', 'Abandoned')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )


    def __str__(self):
        return f"{self.athlete.full_name} - {self.goal_type}"



def get_role_display(self):
    role_dict = dict(self.ROLE_CHOICES)
    return role_dict.get(self.role, self.role)