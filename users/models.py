from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    CITIZEN = 'CITIZEN'
    OFFICER = 'OFFICER'
    ADMIN = 'ADMIN'

    ROLE_CHOICES = [
        (CITIZEN, 'Citizen'),
        (OFFICER, 'Revenue Officer'),
        (ADMIN, 'Revenue Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CITIZEN)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_citizen(self):
        return self.role == self.CITIZEN

    def is_officer(self):
        return self.role == self.OFFICER

    def is_admin(self):
        return self.role == self.ADMIN

    def get_role_display_name(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    def __str__(self):
        return f"{self.username} ({self.role})"


class OfficerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='officer_profile')
    designation = models.CharField(max_length=100, default='Revenue Officer')
    workload_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True)
    admin_remarks = models.TextField(blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.designation} (Workload: {self.workload_count})"

    def get_completion_rate(self):
        from applications.models import CertificateApplication
        total = CertificateApplication.objects.filter(assigned_officer=self).count()
        done = CertificateApplication.objects.filter(
            assigned_officer=self,
            status__in=['APPROVED', 'REJECTED']
        ).count()
        return round((done / total * 100), 1) if total > 0 else 0
