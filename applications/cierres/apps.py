# applications/cierres/apps.py

"""
Módulo de configuración de la aplicación 'cierres'.

Este archivo define la clase de configuración `CierresConfig`, la cual es utilizada
por Django para identificar y cargar la aplicación dentro del proyecto. Aquí se especifican
parámetros globales como el tipo de campo por defecto para las claves primarias y el
nombre completo de la aplicación.
"""

from django.apps import AppConfig


class CierresConfig(AppConfig):
    """
    Clase de configuración para la aplicación 'cierres'.

    Hereda de `AppConfig` y establece las opciones por defecto para esta aplicación
    específica, asegurando su correcta integración en el ecosistema del proyecto Django.
    """
    
    # Define el tipo de campo automático que se usará para las claves primarias (IDs)
    # de los modelos en esta aplicación, a menos que se especifique lo contrario.
    # 'BigAutoField' es un entero de 64 bits, recomendado para escalabilidad a largo plazo.
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre completo de la aplicación, incluyendo la ruta del paquete.
    # Esto permite a Django localizar la aplicación dentro de la estructura del proyecto.
    name = 'applications.cierres'