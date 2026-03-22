from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, OfficerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'address')}),
    )


@admin.register(OfficerProfile)
class OfficerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'designation', 'workload_count', 'is_active', 'is_flagged']
    list_filter = ['is_active', 'is_flagged']
