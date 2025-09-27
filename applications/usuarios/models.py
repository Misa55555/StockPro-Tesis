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
    nombre_completo = models.CharField('Nombre Completo', max_length=150, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')

    USERNAME_FIELD = 'email'
    # 'username' es requerido por defecto en AbstractUser, así que lo incluimos.
    REQUIRED_FIELDS = ['username', 'nombre_completo']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['email']

    def save(self, *args, **kwargs):
        # Si el username está vacío al guardar, se copia el email.
        if not self.username:
            self.username = self.email
        
        # Lógica de permisos automáticos
        if self.rol:
            if self.rol.nombre in ['Administrador', 'Vendedor']:
                self.is_staff = True
            else:
                self.is_staff = False
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

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