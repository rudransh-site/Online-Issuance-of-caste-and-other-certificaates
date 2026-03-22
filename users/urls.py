from django.urls import path
from users import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('users/login/', views.login_view, name='login'),
    path('users/logout/', views.logout_view, name='logout'),
    path('users/register/', views.register_view, name='register'),
    path('users/dashboard/', views.dashboard_view, name='dashboard'),
    path('users/profile/', views.profile_view, name='profile'),
]
