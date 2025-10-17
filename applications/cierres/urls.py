# applications/cierres/urls.py
from django.urls import path
from . import views

app_name = 'cierres_app'

urlpatterns = [
    path('realizar-cierre/', views.RealizarCierreView.as_view(), name='realizar_cierre'),
]