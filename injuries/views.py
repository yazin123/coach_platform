from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from django.http import HttpResponseRedirect
from datetime import timedelta

from users.models import Athlete, Injury, Physiotherapist, TrainingSession
from .forms import InjuryForm, TreatmentNoteForm, InjuryUpdateForm
from .models import TreatmentNote

@login_required
def injury_list(request):
    """View for listing all injuries, with filters by status, athlete, etc."""
    # Permission check - only physios, coaches, and athletes can view
    if request.user.role not in ['physio', 'coach', 'athlete']:
        raise PermissionDenied()
    
    # Different queries based on user role
    if request.user.role == 'physio':
        # Physiotherapists can see all injuries they're assigned to or unassigned ones
        injuries = Injury.objects.filter(
            Q(physiotherapist=request.user.physiotherapist) | Q(physiotherapist__isnull=True)
        ).select_related('athlete', 'physiotherapist')
        
        # Get all athletes for filter dropdown
        athletes = Athlete.objects.all()
        
    elif request.user.role == 'coach':
        # Coaches can see injuries of athletes they train
        # First, get training sessions created by this coach
        training_sessions = TrainingSession.objects.filter(coach=request.user.coach)
        # Then, get unique athletes from those sessions
        coached_athletes = training_sessions.values_list('athlete__user', flat=True).distinct()
        injuries = Injury.objects.filter(athlete__user__in=coached_athletes).select_related('athlete', 'physiotherapist')
        
        # Get coached athletes for filter dropdown
        athletes = Athlete.objects.filter(user__in=coached_athletes)
        
    else:  # Athletes can only see their own injuries
        injuries = Injury.objects.filter(athlete=request.user.athlete).select_related('physiotherapist')
        athletes = []
    
    # Calculate recovery progress and days until recovery for each injury
    for injury in injuries:
        if injury.status != 'resolved':
            # Calculate days between injury date and expected recovery
            total_recovery_days = (injury.expected_recovery_date - injury.injury_date).days
            
            # Calculate days between today and expected recovery
            today = timezone.now().date()
            days_until_recovery = (injury.expected_recovery_date - today).days
            
            # Calculate progress percentage
            if total_recovery_days > 0:
                days_elapsed = total_recovery_days - days_until_recovery
                recovery_progress = min(100, int((days_elapsed / total_recovery_days) * 100))
                
                # Adjust progress based on status
                if injury.status == 'active':
                    recovery_progress = min(30, recovery_progress)  # Cap active injuries at 30%
                
                injury.recovery_progress = recovery_progress
            else:
                injury.recovery_progress = 0
                
            injury.days_until_recovery = days_until_recovery
    
    # Get unique injury types for filter
    injury_types = Injury.objects.values_list('injury_type', flat=True).distinct()
    
    # Calculate statistics
    active_count = injuries.filter(status='active').count()
    recovering_count = injuries.filter(status='recovering').count()
    resolved_count = injuries.filter(status='resolved').count()
    
    # Calculate average recovery time (for resolved injuries)
    resolved_injuries = injuries.filter(status='resolved')
    avg_recovery_days = None
    if resolved_injuries.exists():
        # Try to calculate average recovery time for injuries that have a resolution_date
        injuries_with_resolution = resolved_injuries.exclude(resolution_date__isnull=True)
        
        if injuries_with_resolution.exists():
            total_days = 0
            count = 0
            
            for injury in injuries_with_resolution:
                recovery_time = (injury.resolution_date - injury.injury_date).days
                if recovery_time > 0:
                    total_days += recovery_time
                    count += 1
            
            if count > 0:
                avg_recovery_days = total_days / count
    
    context = {
        'injuries': injuries,
        'athletes': athletes,
        'injury_types': injury_types,
        'active_count': active_count,
        'recovering_count': recovering_count,
        'resolved_count': resolved_count,
        'avg_recovery_days': avg_recovery_days
    }
    
    return render(request, 'injuries/injury_list.html', context)

@login_required
def add_injury(request):
    """View for adding a new injury record."""
    # Only physiotherapists can add injuries
    if request.user.role != 'physio':
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = InjuryForm(request.POST)
        if form.is_valid():
            injury = form.save(commit=False)
            
            # Handle "Other" injury type
            if form.cleaned_data.get('injury_type') == 'Other':
                injury.injury_type = form.cleaned_data.get('other_injury_type')
            
            # Set the physiotherapist to the current user
            injury.physiotherapist = request.user.physiotherapist
            
            # Set the status based on the form
            injury.status = form.cleaned_data.get('status')
            
            # If status is "resolved", set resolution date
            if injury.status == 'resolved':
                injury.resolution_date = timezone.now().date()
                
            # Save the injury
            injury.save()
            
            # Add initial treatment note if notes were provided
            notes = form.cleaned_data.get('notes')
            if notes:
                TreatmentNote.objects.create(
                    injury=injury,
                    title="Initial Assessment",
                    date=timezone.now().date(),
                    content=notes,
                    created_by=request.user
                )
            
            messages.success(request, 'Injury record created successfully!')
            return redirect('injury_detail', injury_id=injury.id)
    else:
        form = InjuryForm()
    
    # Get all athletes for form dropdown
    athletes = Athlete.objects.all()
    
    return render(request, 'injuries/add_injury.html', {'form': form, 'athletes': athletes})

@login_required
def injury_detail(request, injury_id):
    """View for displaying injury details."""
    # Get the injury or 404
    injury = get_object_or_404(Injury, id=injury_id)
    
    # Permission check - physios can see all, coaches can see their athletes, athletes only their own
    if request.user.role == 'physio':
        # Physiotherapists can see any injury
        pass
    elif request.user.role == 'coach':
        # Coaches can see injuries of athletes they train
        training_sessions = TrainingSession.objects.filter(coach=request.user.coach)
        coached_athletes = training_sessions.values_list('athlete__user', flat=True).distinct()
        if injury.athlete.user.id not in coached_athletes:
            raise PermissionDenied()
    elif request.user.role == 'athlete':
        # Athletes can only see their own injuries
        if injury.athlete != request.user.athlete:
            raise PermissionDenied()
    else:
        raise PermissionDenied()
    
    # Calculate recovery progress and days until recovery
    if injury.status != 'resolved':
        # Calculate days between injury date and expected recovery
        total_recovery_days = (injury.expected_recovery_date - injury.injury_date).days
        
        # Calculate days between today and expected recovery
        today = timezone.now().date()
        days_until_recovery = (injury.expected_recovery_date - today).days
        
        # Calculate progress percentage
        if total_recovery_days > 0:
            days_elapsed = total_recovery_days - days_until_recovery
            recovery_progress = min(100, int((days_elapsed / total_recovery_days) * 100))
            
            # Adjust progress based on status
            if injury.status == 'active':
                recovery_progress = min(30, recovery_progress)  # Cap active injuries at 30%
            
            injury.recovery_progress = recovery_progress
        else:
            injury.recovery_progress = 0
            
        injury.days_until_recovery = days_until_recovery
    
    # Get treatment notes for this injury
    treatment_notes = TreatmentNote.objects.filter(injury=injury).order_by('-date')
    
    # Get related training sessions for context
    related_sessions = TrainingSession.objects.filter(
        athlete=injury.athlete,
        session_date__gte=injury.injury_date
    ).order_by('session_date')[:5]
    
    # For status update timeline
    timeline_events = []
    
    # Add recovery start event if in recovering status
    if injury.status in ['recovering', 'resolved'] and hasattr(injury, 'recovery_start_date'):
        timeline_events.append({
            'title': 'Recovery Started',
            'date': injury.recovery_start_date,
            'description': 'Injury status changed from active to recovering.'
        })
    
    # Add resolution event if resolved
    if injury.status == 'resolved' and hasattr(injury, 'resolution_date'):
        timeline_events.append({
            'title': 'Injury Resolved',
            'date': injury.resolution_date,
            'description': 'Athlete has fully recovered from this injury.'
        })
    
    context = {
        'injury': injury,
        'treatment_notes': treatment_notes,
        'related_sessions': related_sessions,
        'timeline_events': timeline_events,
        'today': timezone.now().date()
    }
    
    return render(request, 'injuries/injury_detail.html', context)

@login_required
def update_injury(request, injury_id):
    """View for updating an existing injury record."""
    # Only physiotherapists can update injuries
    if request.user.role != 'physio':
        raise PermissionDenied()
    
    # Get the injury or 404
    injury = get_object_or_404(Injury, id=injury_id)
    
    if request.method == 'POST':
        form = InjuryUpdateForm(request.POST, instance=injury)
        if form.is_valid():
            updated_injury = form.save(commit=False)
            
            # Handle "Other" injury type
            if form.cleaned_data.get('injury_type') == 'Other':
                updated_injury.injury_type = form.cleaned_data.get('other_injury_type')
            
            # Check if status changed and handle accordingly
            old_status = injury.status
            new_status = form.cleaned_data.get('status')
            
            if old_status != new_status:
                # If changing to recovering, set recovery start date
                if new_status == 'recovering' and old_status == 'active':
                    updated_injury.recovery_start_date = timezone.now().date()
                
                # If changing to resolved, set resolution date
                if new_status == 'resolved':
                    updated_injury.resolution_date = timezone.now().date()
            
            # Save the updated injury
            updated_injury.save()
            
            # Add update note if provided
            update_notes = form.cleaned_data.get('update_notes')
            if update_notes:
                status_change = old_status != new_status
                title = f"Status Changed to {updated_injury.get_status_display()}" if status_change else "Record Updated"
                
                TreatmentNote.objects.create(
                    injury=updated_injury,
                    title=title,
                    date=timezone.now().date(),
                    content=update_notes,
                    created_by=request.user
                )
            
            messages.success(request, 'Injury record updated successfully!')
            return redirect('injury_detail', injury_id=updated_injury.id)
    else:
        form = InjuryUpdateForm(instance=injury)
    
    return render(request, 'injuries/update_injury.html', {'form': form, 'injury': injury})

@login_required
def mark_injury_resolved(request, injury_id):
    """Quick action to mark an injury as resolved."""
    # Only physiotherapists can resolve injuries
    if request.user.role != 'physio':
        raise PermissionDenied()
    
    # Get the injury or 404
    injury = get_object_or_404(Injury, id=injury_id)
    
    # Update status and set resolution date
    injury.status = 'resolved'
    injury.resolution_date = timezone.now().date()
    injury.save()
    
    # Create a note for the resolution
    TreatmentNote.objects.create(
        injury=injury,
        title="Injury Resolved",
        date=timezone.now().date(),
        content="Athlete has fully recovered from this injury.",
        created_by=request.user
    )
    
    messages.success(request, 'Injury has been marked as resolved!')
    return redirect('injury_detail', injury_id=injury.id)

@login_required
def add_treatment_note(request, injury_id):
    """Add a treatment note to an injury."""
    # Only physiotherapists can add treatment notes
    if request.user.role != 'physio':
        raise PermissionDenied()
    
    # Get the injury or 404
    injury = get_object_or_404(Injury, id=injury_id)
    
    if request.method == 'POST':
        form = TreatmentNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.injury = injury
            note.created_by = request.user
            note.save()
            
            messages.success(request, 'Treatment note added successfully!')
    else:
        messages.error(request, 'Invalid form submission.')
    
    return redirect('injury_detail', injury_id=injury.id)

@login_required
def update_injury_status(request, injury_id):
    """Update the status of an injury and its progress."""
    # Only physiotherapists can update injury status
    if request.user.role != 'physio':
        raise PermissionDenied()
    
    # Get the injury or 404
    injury = get_object_or_404(Injury, id=injury_id)
    
    if request.method == 'POST':
        # Get form data
        new_status = request.POST.get('status')
        recovery_progress = request.POST.get('recovery_progress')
        expected_recovery_date = request.POST.get('expected_recovery_date')
        notes = request.POST.get('notes')
        
        # Validate the status
        if new_status not in ['active', 'recovering', 'resolved']:
            messages.error(request, 'Invalid status value.')
            return redirect('injury_detail', injury_id=injury.id)
        
        # Check if status changed
        status_changed = injury.status != new_status
        
        # Update the injury
        injury.status = new_status
        
        # If changing to recovering, set recovery start date
        if status_changed and new_status == 'recovering' and injury.status == 'active':
            injury.recovery_start_date = timezone.now().date()
        
        # If changing to resolved, set resolution date
        if new_status == 'resolved':
            injury.resolution_date = timezone.now().date()
        
        # Update expected recovery date if provided
        if expected_recovery_date:
            try:
                injury.expected_recovery_date = expected_recovery_date
            except ValueError:
                messages.error(request, 'Invalid date format for expected recovery date.')
                return redirect('injury_detail', injury_id=injury.id)
        
        # Save the updated injury
        injury.save()
        
        # Add a treatment note about the status update if notes were provided
        if notes:
            title = f"Status Updated to {injury.get_status_display()}" if status_changed else "Progress Update"
            
            TreatmentNote.objects.create(
                injury=injury,
                title=title,
                date=timezone.now().date(),
                content=notes,
                created_by=request.user
            )
        
        messages.success(request, 'Injury status updated successfully!')
    
    return redirect('injury_detail', injury_id=injury.id)