# applications/usuarios/apps.py

"""
Módulo de configuración de la aplicación 'usuarios'.

Este archivo define la clase de configuración `UsuariosConfig`, utilizada por Django
para la inicialización y registro de la aplicación de gestión de usuarios.
Establece parámetros fundamentales como el sistema de auto-incremento para claves
primarias y el identificador único de la aplicación dentro del proyecto.
"""

from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    """
    Clase de configuración para la aplicación 'usuarios'.

    Hereda de `AppConfig` y define las directivas de configuración específicas para
    el módulo de autenticación y perfiles de usuario. Su presencia permite que Django
    reconozca e integre esta aplicación en el sistema.
    """
    
    # Define el tipo de campo automático predeterminado para las claves primarias (IDs)
    # de los modelos de esta aplicación. 'BigAutoField' garantiza un entero de 64 bits,
    # ofreciendo escalabilidad para grandes volúmenes de usuarios y registros.
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre completo de la aplicación, incluyendo la ruta del paquete (namespace).
    # Este identificador es utilizado por Django para cargar modelos, migraciones
    # y otros recursos asociados a la aplicación.
    name = 'applications.usuarios'