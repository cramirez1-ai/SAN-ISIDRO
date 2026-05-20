"""
URL configuration for barangay_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('announcements/', views.announcements, name='announcements'),
    path('contact/', views.contact, name='contact'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/requests/', views.user_requests, name='user_requests'),
    path('user/complaints/', views.user_complaints, name='user_complaints'),
    path('user/feedback/', views.user_feedback, name='user_feedback'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/<str:section>/', views.admin_list, name='admin_list'),
    path('manage/<str:section>/add/', views.admin_add, name='admin_add'),
    path('manage/<str:section>/<int:pk>/edit/', views.admin_edit, name='admin_edit'),
    path('manage/<str:section>/<int:pk>/delete/', views.admin_delete, name='admin_delete'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
