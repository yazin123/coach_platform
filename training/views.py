# training/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from users.models import Athlete, TrainingSession
from .forms import TrainingSessionForm

@login_required
def create_training_session(request):
    # Only coaches can create training sessions
    if request.user.role != 'coach':
        raise PermissionDenied()
    
    # Get all athletes for the coach to select from
    athletes = Athlete.objects.all()
    
    if request.method == 'POST':
        form = TrainingSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.coach = request.user.coach
            session.save()
            messages.success(request, 'Training session created successfully!')
            return redirect('training_session_list')
    else:
        form = TrainingSessionForm()
    
    return render(request, 'training/create_session.html', {
        'form': form, 
        'athletes': athletes
    })

@login_required
def training_session_list(request):
    # Coaches see all their sessions
    # Athletes see sessions they are part of
    if request.user.role == 'coach':
        sessions = TrainingSession.objects.filter(coach=request.user.coach)
    elif request.user.role == 'athlete':
        sessions = TrainingSession.objects.filter(athlete=request.user.athlete)
    else:
        sessions = []
    
    return render(request, 'training/session_list.html', {'sessions': sessions})

@login_required
def training_session_detail(request, session_id):
    try:
        session = TrainingSession.objects.get(id=session_id)
        
        # Check user's permission to view this session
        if request.user.role == 'athlete' and session.athlete != request.user.athlete:
            raise PermissionDenied()
        elif request.user.role == 'coach' and session.coach != request.user.coach:
            raise PermissionDenied()
        
        return render(request, 'training/session_detail.html', {'session': session})
    except TrainingSession.DoesNotExist:
        messages.error(request, 'Training session not found')
        return redirect('training_session_list')