# applications/stock/apps.py

"""
Módulo de configuración de la aplicación 'stock'.

Este archivo define la clase de configuración `StockConfig`, la cual es utilizada
por Django para identificar, cargar y configurar la aplicación de gestión de inventario
dentro del proyecto. Establece parámetros globales como el tipo de campo
por defecto para las claves primarias y el nombre completo de la aplicación.
"""

from django.apps import AppConfig


class StockConfig(AppConfig):
    """
    Clase de configuración para la aplicación 'stock'.

    Hereda de `AppConfig` y define las opciones de configuración específicas para
    esta aplicación, asegurando su correcta inicialización e integración en el
    ecosistema del proyecto Django.
    """
    
    # Define el tipo de campo automático que se utilizará para las claves primarias (IDs)
    # de los modelos en esta aplicación. 'BigAutoField' es un entero de 64 bits,
    # lo que proporciona un rango de IDs significativamente mayor que 'AutoField'.
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre completo de la aplicación, incluyendo la ruta del paquete (namespace).
    # Esto es crucial para que Django localice correctamente la aplicación y sus recursos.
    name = 'applications.stock'