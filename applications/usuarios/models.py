# applications/usuarios/models.py

"""
Módulo de Modelos para la aplicación 'usuarios'.

Este archivo define las estructuras de datos fundamentales para la gestión de usuarios,
roles y clientes dentro del sistema. Se establece una arquitectura que extiende el modelo
de usuario por defecto de Django para adaptarlo a las necesidades específicas del
punto de venta, incluyendo una clara separación de roles y la capacidad de asociar
información adicional a los clientes finales.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    """
    Representa los roles que pueden ser asignados a los usuarios en el sistema.
    
    Este modelo permite crear y gestionar los diferentes niveles de acceso y permisos,
    como 'Administrador', 'Vendedor' o 'Cliente', desacoplando la lógica de permisos
    del modelo de usuario principal.
    """
    # Campo para el nombre único del rol (ej. "Administrador").
    nombre = models.CharField(
        'Nombre del Rol', 
        max_length=50, 
        unique=True  # Asegura que no haya roles con el mismo nombre.
    )
    # Campo opcional para una descripción más detallada de las responsabilidades del rol.
    descripcion = models.TextField(
        'Descripción', 
        blank=True
    )

    class Meta:
        """
        Metadatos para el modelo Rol.
        Define cómo se presenta el modelo en el panel de administración de Django
        y el orden por defecto de los registros.
        """
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']  # Ordena los roles alfabéticamente por nombre.

    def __str__(self):
        """
        Representación en cadena de texto del objeto Rol.
        Retorna el nombre del rol, facilitando su identificación en el panel de
        administración y otras interfaces.
        """
        return self.nombre

class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado que extiende la clase AbstractUser de Django.

    Este modelo reemplaza el comportamiento de autenticación por defecto (basado en
    'username') para utilizar el correo electrónico como identificador principal,
    lo cual es una práctica moderna y más intuitiva para los usuarios. Además,
    se le asocia un 'Rol' para gestionar los permisos de manera centralizada.
    """
    # Campo de correo electrónico, definido como único en el sistema.
    email = models.EmailField(
        'Correo Electrónico', 
        unique=True
    )
    # Campo para almacenar el nombre completo del usuario.
    nombre_completo = models.CharField(
        'Nombre Completo', 
        max_length=150, 
        blank=True
    )
    # Relación con el modelo Rol. Un usuario tiene un único rol.
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.SET_NULL,  # Si se elimina un rol, el campo en Usuario se pone nulo.
        null=True, 
        blank=True, 
        related_name='usuarios'
    )

    # Configuración para la autenticación: el email será el campo de login.
    USERNAME_FIELD = 'email'
    # Campos requeridos al crear un usuario desde la consola (createsuperuser).
    REQUIRED_FIELDS = ['username', 'nombre_completo']

    class Meta:
        """
        Metadatos para el modelo Usuario.
        """
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['email']  # Ordena los usuarios por su correo electrónico.

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método de guardado para añadir lógica de negocio personalizada.

        1.  Asegura que el campo 'username' (requerido por Django) se complete
            automáticamente con el valor del email si no se proporciona.
        2.  Asigna permisos de acceso al panel de administración (`is_staff`)
            basándose en el rol asignado.
        """
        # Si el username está vacío al guardar, se copia el email.
        if not self.username:
            self.username = self.email
        
        # Lógica de permisos automáticos basada en el rol.
        if self.rol:
            # Los roles 'Administrador' y 'Vendedor' tienen acceso al panel interno.
            if self.rol.nombre in ['Administrador', 'Vendedor']:
                self.is_staff = True
            else:
                self.is_staff = False
        
        # Llama al método save() original de la clase padre para completar el guardado.
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Representación en cadena de texto del objeto Usuario.
        Retorna el email del usuario como su identificador principal.
        """
        return self.email

class Cliente(models.Model):
    """
    Modelo que extiende la información del Usuario para perfiles de Cliente Final.
    
    Este modelo almacena datos específicos del cliente, como su DNI y teléfono,
    manteniendo una relación uno a uno con el modelo Usuario. Esta separación
    permite mantener el modelo Usuario limpio y enfocado en la autenticación,
    mientras que este modelo gestiona la información comercial del cliente.
    """
    # Relación uno a uno con Usuario. Un cliente es un usuario y viceversa.
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,  # Si se elimina el Usuario, se elimina el Cliente asociado.
        primary_key=True
    )
    # Documento Nacional de Identidad del cliente, debe ser único.
    dni = models.CharField(
        'DNI', 
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True
    )
    # Número de teléfono de contacto del cliente.
    telefono = models.CharField(
        'Teléfono', 
        max_length=30, 
        blank=True, 
        null=True
    )

    class Meta:
        """
        Metadatos para el modelo Cliente.
        """
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        # Ordena los clientes alfabéticamente por el nombre completo del usuario asociado.
        ordering = ['usuario__nombre_completo']

    def __str__(self):
        """
        Representación en cadena de texto del objeto Cliente.
        Retorna el nombre completo del usuario asociado para una fácil identificación.
        """
        return self.usuario.nombre_completo