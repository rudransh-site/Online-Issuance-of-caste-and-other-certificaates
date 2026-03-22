from django.urls import path
from admin_panel import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('officers/', views.manage_officers, name='manage_officers'),
    path('officers/<int:pk>/toggle/', views.toggle_officer, name='toggle_officer'),
    path('officers/<int:pk>/remark/', views.add_remark, name='add_remark'),
    path('officers/<int:pk>/flag/', views.flag_officer, name='flag_officer'),
    path('applications/', views.all_applications, name='all_applications'),
    path('audit-log/', views.audit_log, name='audit_log'),
]
