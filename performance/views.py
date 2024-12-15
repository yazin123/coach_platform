# performance/views.py (Updated)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from users.models import PerformanceLog, Goal
from .forms import PerformanceLogForm, GoalForm
from django.db.models import Avg, Sum

@login_required
def log_performance(request):
    # Only athletes can log performance
    if request.user.role != 'athlete':
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = PerformanceLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.athlete = request.user.athlete
            log.save()
            messages.success(request, 'Performance logged successfully!')
            return redirect('performance_history')
    else:
        form = PerformanceLogForm()
    
    return render(request, 'performance/log_performance.html', {'form': form})

@login_required
def performance_history(request):
    # Only athletes can view their performance history
    if request.user.role != 'athlete':
        raise PermissionDenied()
    
    logs = PerformanceLog.objects.filter(athlete=request.user.athlete).order_by('-log_date')
    
    # Basic analytics
    total_sessions = logs.count()
    avg_intensity = logs.aggregate(Avg('intensity_level'))['intensity_level__avg'] or 0
    total_duration = logs.aggregate(Sum('duration'))['duration__sum'] or 0
    
    context = {
        'logs': logs,
        'total_sessions': total_sessions,
        'avg_intensity': round(avg_intensity, 2),
        'total_duration': round(total_duration, 2)
    }
    
    return render(request, 'performance/performance_history.html', context)

@login_required
def set_goal(request):
    # Only athletes can set goals
    if request.user.role != 'athlete':
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.athlete = request.user.athlete
            goal.save()
            messages.success(request, 'Goal set successfully!')
            return redirect('goal_list')
    else:
        form = GoalForm()
    
    return render(request, 'performance/set_goal.html', {'form': form})

@login_required
def goal_list(request):
    # Only athletes can view their goals
    if request.user.role != 'athlete':
        raise PermissionDenied()
    
    goals = Goal.objects.filter(athlete=request.user.athlete).order_by('target_date')
    return render(request, 'performance/goal_list.html', {'goals': goals})

@login_required
def goal_detail(request, goal_id):
    # Only athletes can view their goal details
    if request.user.role != 'athlete':
        raise PermissionDenied()
    
    goal = get_object_or_404(Goal, id=goal_id, athlete=request.user.athlete)
    return render(request, 'performance/goal_detail.html', {'goal': goal})

@login_required
def update_goal_status(request, goal_id):
    # Only athletes can update goal status
    if request.user.role != 'athlete':
        raise PermissionDenied()
    
    goal = get_object_or_404(Goal, id=goal_id, athlete=request.user.athlete)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Goal.STATUS_CHOICES):
            goal.status = new_status
            goal.save()
            messages.success(request, 'Goal status updated successfully!')
            return redirect('goal_detail', goal_id=goal.id)
    
    return render(request, 'performance/update_goal_status.html', {'goal': goal})