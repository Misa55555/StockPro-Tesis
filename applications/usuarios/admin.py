# applications/usuarios/admin.py

"""
Módulo de configuración del Panel de Administración para la aplicación 'usuarios'.

Este archivo define la interfaz de gestión para el modelo de usuario personalizado (`Usuario`),
así como para los roles (`Rol`) y perfiles de clientes (`Cliente`).
Se implementa una lógica avanzada para la administración de usuarios, diferenciando
entre los formularios de creación y edición para garantizar la seguridad en el manejo
de contraseñas y una mejor organización de la información.
"""

from django.contrib import admin
from .models import Rol, Usuario, Cliente
from .forms import UsuarioCreationForm, UsuarioChangeForm

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """
    Configuración avanzada para la administración del modelo Usuario.

    Esta clase personaliza el comportamiento del admin de Django para manejar
    correctamente el ciclo de vida de los usuarios personalizados.
    Aspectos clave:
    - Uso de formularios distintos para creación (con password) y edición (sin password directo).
    - Organización de campos en secciones (fieldsets).
    - Interceptación del guardado para asegurar el hasheo de contraseñas.
    """
    
    # Definición de formularios específicos para cada acción.
    add_form = UsuarioCreationForm # Utilizado solo al crear un nuevo usuario.
    form = UsuarioChangeForm       # Utilizado para modificar usuarios existentes.
    
    # Configuración de la lista de usuarios.
    list_display = ('email', 'username', 'nombre_completo', 'rol', 'is_staff')
    search_fields = ('email', 'username', 'nombre_completo')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')

    def get_fieldsets(self, request, obj=None):
        """
        Define dinámicamente la estructura del formulario según el contexto.

        Args:
            request: La solicitud HTTP actual.
            obj: El objeto usuario actual (None si se está creando uno nuevo).

        Returns:
            tuple: La configuración de fieldsets adecuada.
        """
        if not obj:  # Caso: Creación de un nuevo usuario.
            # Se muestran los campos esenciales y la contraseña por duplicado.
            return (
                (None, {'fields': ('username', 'email', 'nombre_completo', 'rol', 'password', 'password2')}),
            )
        
        # Caso: Edición de un usuario existente.
        # Se oculta la contraseña (se cambia por otro mecanismo) y se organizan los datos.
        return ( 
            (None, {'fields': ('username', 'email')}),
            ('Información Personal', {'fields': ('nombre_completo', 'rol')}),
            ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        )

    def get_form(self, request, obj=None, **kwargs):
        """
        Selecciona la clase de formulario apropiada.

        Sobrescribe el método base para inyectar `add_form` cuando se está creando
        un registro, garantizando que las validaciones de contraseña de creación se apliquen.
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def save_model(self, request, obj, form, change):
        """
        Maneja la persistencia del modelo asegurando la seguridad de la contraseña.

        Django no hashea las contraseñas automáticamente cuando se usa un ModelForm estándar
        en el admin personalizado de esta manera. Este método intercepta el guardado
        para invocar `set_password`, que aplica el algoritmo de hash (pbkdf2 por defecto).
        """
        if 'password' in form.cleaned_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """
    Configuración simple para la administración de Roles.
    Permite visualizar y gestionar los roles disponibles en el sistema (ej. Administrador, Vendedor).
    """
    list_display = ('nombre',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuración para la administración de perfiles de Cliente.
    Permite visualizar la relación entre el perfil de cliente y el usuario base.
    """
    list_display = ('usuario',)