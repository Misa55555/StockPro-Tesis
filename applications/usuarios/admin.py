# applications/usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Rol, Usuario, Cliente

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Solo definimos lo que queremos ver, el resto lo maneja Django.
    list_display = ('email', 'nombre_completo', 'rol', 'is_staff')

    # Usamos los fieldsets por defecto de UserAdmin.
    # Esto es más estable.
    fieldsets = UserAdmin.fieldsets
    add_fieldsets = UserAdmin.add_fieldsets

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario',)