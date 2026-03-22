from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import User, OfficerProfile
from applications.models import CertificateApplication
from automation.models import AuditLog, SystemConfiguration
from automation.services import AuditService, OverdueService


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            messages.error(request, 'Access denied. Admin only.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def dashboard(request):
    OverdueService.check_and_mark_overdue()

    total = CertificateApplication.objects.count()
    submitted = CertificateApplication.objects.filter(status='SUBMITTED').count()
    assigned = CertificateApplication.objects.filter(status='ASSIGNED').count()
    approved = CertificateApplication.objects.filter(status='APPROVED').count()
    rejected = CertificateApplication.objects.filter(status='REJECTED').count()
    overdue = CertificateApplication.objects.filter(status='OVERDUE').count()

    completed = approved + rejected
    completion_pct = round((completed / total * 100), 1) if total > 0 else 0

    officers = OfficerProfile.objects.select_related('user').all()
    recent_logs = AuditLog.objects.select_related('performed_by', 'application')[:10]
    recent_apps = CertificateApplication.objects.select_related('citizen', 'assigned_officer')[:8]

    return render(request, 'admin_panel/dashboard.html', {
        'total': total,
        'submitted': submitted,
        'assigned': assigned,
        'approved': approved,
        'rejected': rejected,
        'overdue': overdue,
        'completion_pct': completion_pct,
        'officers': officers,
        'recent_logs': recent_logs,
        'recent_apps': recent_apps,
    })


@login_required
@admin_required
def manage_officers(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        designation = request.POST.get('designation', 'Revenue Officer').strip()

        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=User.OFFICER
            )
            OfficerProfile.objects.create(user=user, designation=designation)
            AuditService.log(
                performed_by=request.user,
                action='OFFICER_CREATED',
                description=f"Officer account created: {username}"
            )
            messages.success(request, f'Officer "{username}" created successfully.')
            return redirect('manage_officers')

    officers = OfficerProfile.objects.select_related('user').all().order_by('-user__date_joined')
    return render(request, 'admin_panel/officers.html', {'officers': officers})


@login_required
@admin_required
def toggle_officer(request, pk):
    officer = get_object_or_404(OfficerProfile, pk=pk)
    officer.is_active = not officer.is_active
    officer.save()
    status = 'activated' if officer.is_active else 'deactivated'
    messages.success(request, f'Officer {officer.user.username} {status}.')
    return redirect('manage_officers')


@login_required
@admin_required
def add_remark(request, pk):
    officer = get_object_or_404(OfficerProfile, pk=pk)
    if request.method == 'POST':
        remark = request.POST.get('remark', '').strip()
        if remark:
            officer.admin_remarks = remark
            officer.save()
            AuditService.log(
                performed_by=request.user,
                action='REMARK_ADDED',
                description=f"Remark added to {officer.user.username}: {remark}"
            )
            messages.success(request, 'Remark added successfully.')
    return redirect('manage_officers')


@login_required
@admin_required
def flag_officer(request, pk):
    officer = get_object_or_404(OfficerProfile, pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        officer.is_flagged = not officer.is_flagged
        officer.flag_reason = reason if officer.is_flagged else ''
        officer.save()
        status = 'flagged as high performer' if officer.is_flagged else 'unflagged'
        AuditService.log(
            performed_by=request.user,
            action='OFFICER_FLAGGED',
            description=f"Officer {officer.user.username} {status}"
        )
        messages.success(request, f'Officer {officer.user.username} {status}.')
    return redirect('manage_officers')


@login_required
@admin_required
def all_applications(request):
    OverdueService.check_and_mark_overdue()
    status_filter = request.GET.get('status', '')
    applications = CertificateApplication.objects.select_related('citizen', 'assigned_officer__user')
    if status_filter:
        applications = applications.filter(status=status_filter)

    total = CertificateApplication.objects.count()
    overdue_count = CertificateApplication.objects.filter(status='OVERDUE').count()

    return render(request, 'admin_panel/all_applications.html', {
        'applications': applications,
        'status_filter': status_filter,
        'total': total,
        'overdue_count': overdue_count,
    })


@login_required
@admin_required
def audit_log(request):
    logs = AuditLog.objects.select_related('performed_by', 'application').all()
    return render(request, 'admin_panel/audit_log.html', {'logs': logs})
