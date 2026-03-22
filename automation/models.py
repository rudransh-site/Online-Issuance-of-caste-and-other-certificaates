from django.db import models
from django.utils import timezone


class AuditLog(models.Model):
    performed_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs'
    )
    application = models.ForeignKey(
        'applications.CertificateApplication', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audit_logs'
    )
    action = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%d-%m-%Y %H:%M}] {self.action} — {self.performed_by}"


class SystemConfiguration(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def get(cls, key, default=None):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
