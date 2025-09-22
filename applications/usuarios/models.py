# applications/usuarios/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    nombre = models.CharField('Nombre del Rol', max_length=50, unique=True)
    descripcion = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    email = models.EmailField('Correo Electrónico', unique=True)
    nombre_completo = models.CharField('Nombre Completo', max_length=150)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre_completo']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre_completo']

    # --- INICIO DE LA SOLUCIÓN DEFINITIVA ---
    def save(self, *args, **kwargs):
        # Si el username está vacío, lo poblamos con el email antes de guardar.
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
    # --- FIN DE LA SOLUCIÓN DEFINITIVA ---

    def __str__(self):
        return self.nombre_completo

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    dni = models.CharField('DNI', max_length=20, unique=True, blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['usuario__nombre_completo']

    def __str__(self):
        return self.usuario.nombre_completo