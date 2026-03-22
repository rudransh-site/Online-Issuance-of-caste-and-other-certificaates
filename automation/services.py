from django.utils import timezone
from datetime import timedelta


class AssignmentService:
    """Assigns applications to the least-loaded active officer."""

    @staticmethod
    def assign_application(application):
        from users.models import OfficerProfile
        from automation.models import AuditLog

        active_officers = OfficerProfile.objects.filter(is_active=True).order_by('workload_count')
        if not active_officers.exists():
            return False, "No active officers available for assignment."

        officer = active_officers.first()
        application.assigned_officer = officer
        application.assigned_date = timezone.now()
        application.due_date = timezone.now() + timedelta(days=7)
        application.status = 'ASSIGNED'
        application.save()

        officer.workload_count += 1
        officer.save()

        AuditLog.objects.create(
            application=application,
            action='ASSIGNED',
            description=f"Auto-assigned to Officer: {officer.user.get_full_name() or officer.user.username} (workload was {officer.workload_count - 1})"
        )
        return True, f"Assigned to {officer.user.username}"


class ProcessingService:
    """Handles officer approve/reject decisions."""

    @staticmethod
    def approve_application(application, officer_user, remarks=''):
        from automation.models import AuditLog

        application.status = 'APPROVED'
        application.processed_date = timezone.now()
        application.remarks = remarks
        application.save()

        if application.assigned_officer:
            op = application.assigned_officer
            if op.workload_count > 0:
                op.workload_count -= 1
                op.save()

        AuditLog.objects.create(
            performed_by=officer_user,
            application=application,
            action='APPROVED',
            description=f"Application approved by {officer_user.username}. Remarks: {remarks or 'None'}"
        )

    @staticmethod
    def reject_application(application, officer_user, remarks=''):
        from automation.models import AuditLog

        if not remarks or not remarks.strip():
            return False, "Remarks are mandatory for rejection."

        application.status = 'REJECTED'
        application.processed_date = timezone.now()
        application.remarks = remarks
        application.save()

        if application.assigned_officer:
            op = application.assigned_officer
            if op.workload_count > 0:
                op.workload_count -= 1
                op.save()

        AuditLog.objects.create(
            performed_by=officer_user,
            application=application,
            action='REJECTED',
            description=f"Application rejected by {officer_user.username}. Reason: {remarks}"
        )
        return True, "Application rejected."


class OverdueService:
    """Scans assigned applications and marks overdue ones."""

    @staticmethod
    def check_and_mark_overdue():
        from applications.models import CertificateApplication
        from automation.models import AuditLog

        now = timezone.now()
        overdue_apps = CertificateApplication.objects.filter(
            status='ASSIGNED',
            due_date__lt=now
        )
        count = 0
        for app in overdue_apps:
            app.status = 'OVERDUE'
            app.save()
            AuditLog.objects.create(
                application=app,
                action='OVERDUE',
                description=f"Application marked OVERDUE. Due date was {app.due_date:%d-%m-%Y %H:%M}"
            )
            count += 1
        return count


class AuditService:
    """Creates audit log entries."""

    @staticmethod
    def log(action, description='', performed_by=None, application=None):
        from automation.models import AuditLog
        AuditLog.objects.create(
            performed_by=performed_by,
            application=application,
            action=action,
            description=description
        )
