# applications/cierres/urls.py

"""
Configuración de URLs para la aplicación 'cierres'.

Este módulo define el mapeo entre las rutas URL relativas a la gestión de cierres de caja
y las Vistas (Views) correspondientes que procesan las solicitudes. Facilita el enrutamiento
de las peticiones HTTP hacia la lógica de negocio adecuada.
"""

from django.urls import path
from . import views

# Definición del espacio de nombres (namespace) para la aplicación.
# Esto permite referenciar las URLs de esta aplicación de manera única en plantillas
# y controladores (ej. usando 'cierres_app:realizar_cierre').
app_name = 'cierres_app'

urlpatterns = [
    # Ruta para acceder a la interfaz de realización de cierre de caja.
    # Mapea la URL relativa 'realizar-cierre/' a la vista basada en clase RealizarCierreView.
    path('realizar-cierre/', views.RealizarCierreView.as_view(), name='realizar_cierre'),
]