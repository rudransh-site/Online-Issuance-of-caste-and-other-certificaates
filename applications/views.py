from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from applications.models import CertificateApplication
from applications.forms import (
    CasteCertificateForm, IncomeCertificateForm,
    BirthCertificateForm, DeathCertificateForm, OfficerDecisionForm
)
from automation.services import AssignmentService, ProcessingService, AuditService, OverdueService

CERT_FORMS = {
    'CASTE': CasteCertificateForm,
    'INCOME': IncomeCertificateForm,
    'BIRTH': BirthCertificateForm,
    'DEATH': DeathCertificateForm,
}

CERT_LABELS = {
    'CASTE': 'Caste Certificate',
    'INCOME': 'Income Certificate',
    'BIRTH': 'Birth Certificate',
    'DEATH': 'Death Certificate',
}


@login_required
def choose_certificate(request):
    if not request.user.is_citizen():
        messages.error(request, 'Access denied.')
        return redirect('login')
    return render(request, 'applications/choose_certificate.html', {'cert_labels': CERT_LABELS})


@login_required
def submit_application(request, cert_type):
    if not request.user.is_citizen():
        messages.error(request, 'Access denied.')
        return redirect('login')

    cert_type = cert_type.upper()
    if cert_type not in CERT_FORMS:
        messages.error(request, 'Invalid certificate type.')
        return redirect('choose_certificate')

    FormClass = CERT_FORMS[cert_type]
    cert_label = CERT_LABELS[cert_type]

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.citizen = request.user
            application.certificate_type = cert_type
            application.save()

            AuditService.log(
                performed_by=request.user,
                application=application,
                action='SUBMITTED',
                description=f"{request.user.username} submitted {cert_label} application"
            )

            success, msg = AssignmentService.assign_application(application)
            if success:
                messages.success(request, f'Application #{application.id} submitted and assigned to an officer. Expected within 7 days.')
            else:
                messages.warning(request, f'Application submitted but could not be assigned: {msg}')

            return redirect('track_applications')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = FormClass()

    return render(request, 'applications/submit.html', {
        'form': form,
        'cert_type': cert_type,
        'cert_label': cert_label,
    })


@login_required
def track_applications(request):
    if not request.user.is_citizen():
        messages.error(request, 'Access denied.')
        return redirect('login')

    applications = CertificateApplication.objects.filter(citizen=request.user)
    total = applications.count()
    approved = applications.filter(status='APPROVED').count()
    rejected = applications.filter(status='REJECTED').count()
    pending = applications.filter(status__in=['SUBMITTED', 'ASSIGNED', 'OVERDUE']).count()

    return render(request, 'applications/track.html', {
        'applications': applications,
        'total': total, 'approved': approved,
        'rejected': rejected, 'pending': pending,
    })


@login_required
def application_detail_citizen(request, pk):
    application = get_object_or_404(CertificateApplication, pk=pk, citizen=request.user)
    return render(request, 'applications/citizen_detail.html', {'application': application})


# ── OFFICER VIEWS ──

@login_required
def officer_list(request):
    if not request.user.is_officer():
        messages.error(request, 'Access denied.')
        return redirect('login')

    OverdueService.check_and_mark_overdue()

    try:
        profile = request.user.officer_profile
    except Exception:
        messages.error(request, 'Officer profile not found. Contact admin.')
        return redirect('login')

    all_apps = CertificateApplication.objects.filter(assigned_officer=profile)
    overdue = all_apps.filter(status='OVERDUE')
    pending = all_apps.filter(status='ASSIGNED')
    approved = all_apps.filter(status='APPROVED')
    rejected = all_apps.filter(status='REJECTED')

    completion_rate = profile.get_completion_rate()
    show_warning = overdue.count() >= 2

    return render(request, 'applications/officer_list.html', {
        'profile': profile,
        'overdue': overdue, 'pending': pending,
        'approved': approved, 'rejected': rejected,
        'completion_rate': completion_rate,
        'show_warning': show_warning,
    })


@login_required
def officer_detail(request, pk):
    if not request.user.is_officer():
        messages.error(request, 'Access denied.')
        return redirect('login')

    profile = request.user.officer_profile
    application = get_object_or_404(
        CertificateApplication, pk=pk, assigned_officer=profile
    )

    if request.method == 'POST':
        form = OfficerDecisionForm(request.POST)
        if form.is_valid():
            action = request.POST.get('action')
            remarks = form.cleaned_data.get('remarks', '')

            if action == 'APPROVE':
                ProcessingService.approve_application(application, request.user, remarks)
                messages.success(request, f'Application #{application.id} approved.')
                return redirect('officer_list')

            elif action == 'REJECT':
                success, msg = ProcessingService.reject_application(application, request.user, remarks)
                if not success:
                    messages.error(request, msg)
                else:
                    messages.success(request, f'Application #{application.id} rejected.')
                    return redirect('officer_list')
    else:
        form = OfficerDecisionForm()

    return render(request, 'applications/officer_detail.html', {
        'application': application,
        'form': form,
    })


@login_required
def view_certificate(request, pk):
    if not request.user.is_citizen():
        messages.error(request, 'Access denied.')
        return redirect('login')
    application = get_object_or_404(
        CertificateApplication, pk=pk, citizen=request.user, status='APPROVED'
    )
    return render(request, 'applications/certificate.html', {'application': application})
