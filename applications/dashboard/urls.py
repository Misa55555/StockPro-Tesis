# applications/dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard_app'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
]