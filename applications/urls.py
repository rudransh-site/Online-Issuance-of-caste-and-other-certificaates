from django.urls import path
from applications import views

urlpatterns = [
    path('apply/', views.choose_certificate, name='choose_certificate'),
    path('apply/<str:cert_type>/', views.submit_application, name='submit_application'),
    path('track/', views.track_applications, name='track_applications'),
    path('detail/<int:pk>/', views.application_detail_citizen, name='application_detail'),
    path('officer/', views.officer_list, name='officer_list'),
    path('officer/<int:pk>/', views.officer_detail, name='officer_detail'),
    path('certificate/<int:pk>/', views.view_certificate, name='view_certificate'),
]
