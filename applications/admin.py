from django.contrib import admin
from applications.models import CertificateApplication


@admin.register(CertificateApplication)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'applicant_name', 'certificate_type', 'status', 'citizen', 'assigned_officer', 'submitted_date', 'due_date']
    list_filter = ['certificate_type', 'status']
    search_fields = ['applicant_name', 'aadhar_number', 'citizen__username']
    readonly_fields = ['submitted_date']
    list_per_page = 25
