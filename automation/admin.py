from django.contrib import admin
from automation.models import AuditLog, SystemConfiguration

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'action', 'performed_by', 'application']
    list_filter = ['action']
    readonly_fields = ['timestamp']

@admin.register(SystemConfiguration)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
