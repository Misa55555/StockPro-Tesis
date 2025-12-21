# applications/usuarios/models.py

"""
Módulo de Modelos para la aplicación 'usuarios'.

Este archivo define las estructuras de datos fundamentales para la gestión de usuarios,
roles y clientes dentro del sistema.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group  # <--- IMPORTANTE: Importamos Group

class Rol(models.Model):
    """
    Representa los roles que pueden ser asignados a los usuarios en el sistema.
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
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado.
    Extiende AbstractUser y añade lógica de Roles y Grupos automáticos.
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
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='usuarios'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombre_completo']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['email']

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método de guardado para automatizar permisos y grupos.
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
        return self.email

class Cliente(models.Model):
    """
    Modelo que extiende la información del Usuario para perfiles de Cliente Final.
    """
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
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['usuario__nombre_completo']

    def __str__(self):
        return self.usuario.nombre_completo