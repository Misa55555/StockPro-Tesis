# applications/usuarios/forms.py

from django import forms
from .models import Cliente, Usuario

class UsuarioCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirmación de Password', widget=forms.PasswordInput())

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rol')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['password2']

class UsuarioChangeForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rol', 'is_active', 'is_staff', 'is_superuser')

from django.utils import timezone
from .models import Cliente, Usuario

class ClienteForm(forms.ModelForm):
    # Definimos los campos que no están en el modelo Cliente pero que necesitamos en el form
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
        model = Cliente
        fields = ['dni', 'telefono']
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        # Verificamos si ya existe un cliente con ese DNI
        if Cliente.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe un cliente con este DNI.")
        return dni

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Si se proporcionó un email, verificamos que no esté ya en uso
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email

    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        dni = self.cleaned_data.get('dni')
        nombre_completo = self.cleaned_data.get('nombre_completo')
        
        # --- LÓGICA CORREGIDA Y SEGURA ---
        # Si no se proporciona un email, generamos uno único e interno.
        if not email:
            # Usamos el DNI y un timestamp para garantizar la unicidad
            timestamp = int(timezone.now().timestamp())
            generated_email = f"cliente.{dni}.{timestamp}@stockpro.local"
        else:
            generated_email = email

        # Creamos el usuario asociado con el email (real o generado)
        usuario = Usuario(
            username=generated_email, # El username también debe ser único
            nombre_completo=nombre_completo,
            email=generated_email,
            rol_id=3  # ID del Rol 'Cliente'
        )
        usuario.set_unusable_password()
        
        # Guardamos el cliente
        cliente = super().save(commit=False)
        
        if commit:
            usuario.save()
            cliente.usuario = usuario
            cliente.save()
            
        return cliente