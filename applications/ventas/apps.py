# applications/ventas/apps.py

"""
Módulo de configuración de la aplicación de Ventas.

Este archivo define la clase de configuración principal para la aplicación 'ventas',
permitiendo su integración y registro dentro del proyecto Django.
"""

from django.apps import AppConfig


class VentasConfig(AppConfig):
    """
    Clase de configuración para la aplicación Ventas.

    Define los metadatos y configuraciones iniciales requeridas por Django para
    gestionar la aplicación, incluyendo el tipo de campo autoincremental por defecto
    y la ruta completa de importación.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.ventas'