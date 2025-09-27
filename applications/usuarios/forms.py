# applications/usuarios/forms.py

from django import forms
from .models import Usuario

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