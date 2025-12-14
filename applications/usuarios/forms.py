# applications/usuarios/forms.py

"""
Módulo de Formularios para la aplicación 'usuarios'.

Este archivo define los formularios necesarios para la gestión del ciclo de vida
de los usuarios y clientes. Incluye formularios especializados para la creación
y edición de usuarios con validación de contraseñas, así como un formulario
avanzado para el registro de clientes que automatiza la creación de la cuenta
de usuario subyacente.
"""

from django import forms
from django.utils import timezone
from .models import Cliente, Usuario

class UsuarioCreationForm(forms.ModelForm):
    """
    Formulario para la creación de nuevos usuarios.

    Incluye campos dobles para la contraseña con el fin de validar la confirmación
    de la misma antes de persistir el usuario.
    """
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirmación de Password', widget=forms.PasswordInput())

    class Meta:
        """Metadatos de configuración del formulario."""
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rol')

    def clean_password2(self):
        """
        Valida que las dos contraseñas ingresadas coincidan.

        Raises:
            ValidationError: Si 'password' y 'password2' no son idénticos.
        """
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['password2']

class UsuarioChangeForm(forms.ModelForm):
    """
    Formulario para la modificación de usuarios existentes.

    Excluye los campos de contraseña para forzar el uso de mecanismos de cambio
    de contraseña seguros y dedicados. Permite editar datos personales, roles y permisos.
    """
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rol', 'is_active', 'is_staff', 'is_superuser')


class ClienteForm(forms.ModelForm):
    """
    Formulario complejo para la gestión de Clientes.

    Este formulario maneja la creación de una entidad `Cliente` y, simultáneamente,
    la creación automática de su usuario asociado (`Usuario`).
    Permite registrar clientes sin email (generando uno interno) y asegura la integridad
    de datos únicos como el DNI.
    """
    
    # Campos adicionales que no son parte directa del modelo Cliente,
    # pero son necesarios para construir el objeto Usuario asociado.
    nombre_completo = forms.CharField(
        label="Nombre Completo",
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email (Opcional)",
        required=False, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        """Metadatos del formulario ClienteForm."""
        model = Cliente
        fields = ['dni', 'telefono']
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_dni(self):
        """
        Valida la unicidad del Documento Nacional de Identidad (DNI).
        """
        dni = self.cleaned_data.get('dni')
        # Verificamos si ya existe un cliente con ese DNI
        if Cliente.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe un cliente con este DNI.")
        return dni

    def clean_email(self):
        """
        Valida que el correo electrónico, si se proporciona, no esté ya registrado
        por otro usuario en el sistema.
        """
        email = self.cleaned_data.get('email')
        # Si se proporcionó un email, verificamos que no esté ya en uso
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email

    def save(self, commit=True):
        """
        Sobrescribe el método de guardado para manejar la creación dual Usuario-Cliente.

        Lógica implementada:
        1. Genera un email/usuario interno único si no se proporciona uno real.
        2. Crea una instancia de `Usuario` con rol de 'Cliente' (ID 3).
        3. Establece una contraseña no utilizable (el cliente no se loguea al sistema administrativo).
        4. Vincula el nuevo usuario al objeto `Cliente` y guarda ambos.

        Args:
            commit (bool): Si es True, persiste los datos en la base de datos.

        Returns:
            Cliente: La instancia del cliente guardada.
        """
        email = self.cleaned_data.get('email')
        dni = self.cleaned_data.get('dni')
        nombre_completo = self.cleaned_data.get('nombre_completo')
        
        # --- LÓGICA DE GENERACIÓN DE USUARIO ---
        # Si no se proporciona un email, generamos uno único e interno para cumplir
        # con los requisitos del modelo Usuario.
        if not email:
            # Usamos el DNI y un timestamp para garantizar la unicidad absoluta.
            timestamp = int(timezone.now().timestamp())
            generated_email = f"cliente.{dni}.{timestamp}@stockpro.local"
        else:
            generated_email = email

        # Creamos el objeto Usuario en memoria
        usuario = Usuario(
            username=generated_email, # El username también debe ser único
            nombre_completo=nombre_completo,
            email=generated_email,
            rol_id=3  # Asignación forzada del ID del Rol 'Cliente'
        )
        # El usuario no tendrá acceso al sistema mediante login
        usuario.set_unusable_password()
        
        # Preparamos la instancia del cliente sin guardarla aún en BD
        cliente = super().save(commit=False)
        
        if commit:
            # Persistimos primero el usuario para obtener su ID
            usuario.save()
            # Vinculamos y guardamos el cliente
            cliente.usuario = usuario
            cliente.save()
            
        return cliente