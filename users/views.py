from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.forms import CitizenRegisterForm, LoginForm
from automation.services import AuditService


def home_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    return render(request, 'home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                AuditService.log(
                    performed_by=user,
                    action='LOGIN',
                    description=f"{user.username} logged in"
                )
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect_by_role(user)
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        AuditService.log(
            performed_by=request.user,
            action='LOGOUT',
            description=f"{request.user.username} logged out"
        )
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        form = CitizenRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CitizenRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard_view(request):
    return redirect_by_role(request.user)


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


def redirect_by_role(user):
    if user.is_admin():
        return redirect('admin_dashboard')
    elif user.is_officer():
        return redirect('officer_list')
    else:
        return redirect('choose_certificate')
