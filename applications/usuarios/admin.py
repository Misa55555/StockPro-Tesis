# applications/usuarios/admin.py

from django.contrib import admin
from .models import Rol, Usuario, Cliente
from .forms import UsuarioCreationForm, UsuarioChangeForm

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    # Formularios para creación y edición
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    
    list_display = ('email', 'username', 'nombre_completo', 'rol', 'is_staff')
    search_fields = ('email', 'username', 'nombre_completo')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')

    # Usamos get_fieldsets para mostrar campos diferentes al crear y editar
    def get_fieldsets(self, request, obj=None):
        if not obj:  # Si es un objeto nuevo (creación)
            return (
                (None, {'fields': ('username', 'email', 'nombre_completo', 'rol', 'password', 'password2')}),
            )
        return ( # Si es un objeto existente (edición)
            (None, {'fields': ('username', 'email')}),
            ('Información Personal', {'fields': ('nombre_completo', 'rol')}),
            ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        )

    # Sobrescribimos get_form para usar el formulario correcto (add_form al crear)
    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    # Importante: debemos hashear la contraseña manualmente al guardar
    def save_model(self, request, obj, form, change):
        if 'password' in form.cleaned_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario',)