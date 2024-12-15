# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    CustomUserCreationForm, 
    AthleteProfileForm, 
    CoachProfileForm, 
    PhysiotherapistProfileForm, 
    AdminProfileForm
)
from .models import User, Athlete, Coach, Physiotherapist, Admin
from django.db import transaction


@transaction.atomic
def register_view(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        
        # Dynamically select the appropriate profile form based on role
        role = request.POST.get('role')
        
        # Select the right profile form
        if role == 'athlete':
            profile_form = AthleteProfileForm(request.POST)
        elif role == 'coach':
            profile_form = CoachProfileForm(request.POST)
        elif role == 'physio':
            profile_form = PhysiotherapistProfileForm(request.POST)
        elif role == 'admin':
            profile_form = AdminProfileForm(request.POST)
        else:
            messages.error(request, 'Invalid role selected')
            return render(request, 'users/register.html', {'form': user_form})
        
        # Validate both forms
        if user_form.is_valid() and profile_form.is_valid():
            try:
                # Save user first
                user = user_form.save()
                
                # Save profile based on role
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                
                # Authenticate and login
                username = user_form.cleaned_data.get('username')
                raw_password = user_form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                
                messages.success(request, 'Registration successful!')
                return redirect('home')
            
            except Exception as e:
                # If something goes wrong, delete the user to prevent orphaned records
                user.delete()
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            # If forms are not valid, show errors
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request
        user_form = CustomUserCreationForm()
        profile_form = None
    
    return render(request, 'users/register.html', {
        'form': user_form,
        'profile_form': profile_form
    })



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'users/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    
    # Fetch profile based on user role
    try:
        if user.role == 'athlete':
            profile = Athlete.objects.get(user=user)
            form = AthleteProfileForm(instance=profile)
        elif user.role == 'coach':
            profile = Coach.objects.get(user=user)
            form = CoachProfileForm(instance=profile)
        elif user.role == 'physio':
            profile = Physiotherapist.objects.get(user=user)
            form = PhysiotherapistProfileForm(instance=profile)
        elif user.role == 'admin':
            profile = Admin.objects.get(user=user)
            form = AdminProfileForm(instance=profile)
    except Exception as e:
        messages.error(request, 'Profile not found')
        return redirect('home')
    
    return render(request, 'users/profile.html', {
        'user': user,
        'profile': profile,
        'form': form
    })

def home_view(request):
    return render(request, 'home.html')