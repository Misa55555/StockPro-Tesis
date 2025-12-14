# applications/usuarios/models.py

"""
Módulo de Modelos para la aplicación 'usuarios'.

Este archivo define las estructuras de datos fundamentales para la gestión de usuarios,
roles y clientes dentro del sistema. Centraliza la lógica de autenticación y autorización,
extendiendo el modelo de usuario base de Django para incorporar un sistema de Roles
personalizado que se sincroniza automáticamente con los Grupos y Permisos del framework.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group  # <--- IMPORTANTE: Importamos Group

class Rol(models.Model):
    """
    Entidad que representa los roles de seguridad y acceso en el sistema.

    Define los perfiles de usuario (ej. 'Administrador', 'Vendedor', 'Cliente') que
    determinan los permisos y capacidades dentro de la aplicación. Actúa como
    una capa de abstracción sobre los Grupos de Django.
    """
    nombre = models.CharField(
        'Nombre del Rol', 
        max_length=50, 
        unique=True
    )
    descripcion = models.TextField(
        'Descripción', 
        blank=True
    )

    class Meta:
        """Metadatos para la configuración del modelo Rol."""
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']

    def __str__(self):
        """Retorna el nombre del rol como representación del objeto."""
        return self.nombre

class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado que extiende la funcionalidad base de Django.

    Incorpora la gestión de identidad (email como identificador principal) y la
    asociación con un Rol específico. Implementa lógica de negocio crítica en su
    método de guardado para automatizar la asignación de permisos (is_staff) y
    la membresía en Grupos.
    """
    email = models.EmailField(
        'Correo Electrónico', 
        unique=True
    )
    nombre_completo = models.CharField(
        'Nombre Completo', 
        max_length=150, 
        blank=True
    )
    # Relación con el modelo Rol. Si se borra el rol, el usuario permanece pero sin rol (SET_NULL).
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='usuarios'
    )

    # Configuración para usar el email como identificador único de inicio de sesión.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombre_completo']

    class Meta:
        """Metadatos para la configuración del modelo Usuario."""
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['email']

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método de persistencia para aplicar reglas de negocio de seguridad.

        Realiza tres acciones automáticas antes y después de guardar:
        1. Consistencia de datos: Iguala el 'username' al 'email' si no está definido.
        2. Control de acceso (is_staff): Otorga acceso al panel de administración
           basado en el Rol asignado (Solo 'Administrador' tiene acceso por defecto).
        3. Sincronización de Grupos: Asigna al usuario al Grupo de Django correspondiente
           a su Rol, facilitando la gestión de permisos a nivel de framework.
        """
        # 1. Si el username está vacío, usamos el email (corrección de consistencia)
        if not self.username:
            self.username = self.email
        
        # 2. Control de acceso al Panel de Administración (is_staff)
        # Esto decide quién ve la pantalla de administración de Django
        if self.rol:
            if self.rol.nombre == 'Administrador':
                # El Dueño SÍ entra al admin
                self.is_staff = True
            else:
                # El Vendedor NO entra al admin
                self.is_staff = False
        else:
            # Si no tiene rol, quitamos acceso admin (salvo que sea superusuario/ustedes)
            if not self.is_superuser:
                self.is_staff = False
        
        # Guardamos el usuario primero para asegurar que tenga un ID
        super().save(*args, **kwargs)

        # 3. Sincronización con Grupos de Django
        # Esto crea un Grupo con el mismo nombre del Rol y mete al usuario ahí.
        # Sirve para configurar los permisos "finos" (qué puede tocar) desde el panel visual.
        if self.rol:
            # Buscamos o creamos un Grupo de Django con el mismo nombre que el Rol
            group, created = Group.objects.get_or_create(name=self.rol.nombre)
            
            # Limpiamos grupos anteriores y asignamos el nuevo
            self.groups.clear()
            self.groups.add(group)

    def __str__(self):
        """Retorna el email del usuario como su representación."""
        return self.email

class Cliente(models.Model):
    """
    Modelo que extiende la información del Usuario para perfiles de Cliente Final.

    Utiliza una relación One-to-One con el modelo Usuario para almacenar
    datos específicos del dominio de negocio (DNI, Teléfono) que no son 
    necesarios para la autenticación pero sí para la operación comercial (Ventas).
    """
    # Relación uno a uno que vincula este perfil con una cuenta de usuario.
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        primary_key=True
    )
    dni = models.CharField(
        'DNI', 
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True
    )
    telefono = models.CharField(
        'Teléfono', 
        max_length=30, 
        blank=True, 
        null=True
    )

    class Meta:
        """Metadatos para la configuración del modelo Cliente."""
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['usuario__nombre_completo']

    def __str__(self):
        """Retorna el nombre completo del usuario asociado."""
        return self.usuario.nombre_completo