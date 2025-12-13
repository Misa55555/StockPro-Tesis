# applications/dashboard/urls.py

"""
Configuración de URLs para la aplicación 'dashboard'.

Este módulo define el esquema de enrutamiento para el panel de control principal.
Asocia las rutas de acceso web con las Vistas encargadas de calcular y presentar
los indicadores clave de rendimiento (KPIs) y las alertas del sistema.
"""

from django.urls import path
from . import views

# Definición del espacio de nombres (namespace) para la aplicación.
# Permite referenciar las URLs del dashboard de manera única (ej. 'dashboard_app:dashboard')
# en cualquier parte del proyecto, evitando conflictos con otras aplicaciones.
app_name = 'dashboard_app'

urlpatterns = [
    # Ruta principal para acceder al Dashboard.
    # Mapea la URL relativa 'dashboard/' a la vista funcional 'dashboard_view'.
    path('dashboard/', views.dashboard_view, name='dashboard'),
]