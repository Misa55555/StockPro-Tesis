# applications/finanzas/forms.py
from django import forms
from .models import Gasto, CategoriaGasto
from django.utils import timezone

# --- ¡NUEVO! Formulario para la Categoría ---
class CategoriaGastoForm(forms.ModelForm):
    """
    Formulario simple para crear una CategoriaGasto
    desde un modal.
    """
    class Meta:
        model = CategoriaGasto
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Alquiler, Servicios, Sueldos'
            })
        }

# --- Formulario de Gasto (MODIFICADO) ---
class GastoForm(forms.ModelForm):
    """
    Formulario basado en el modelo Gasto para registrar
    nuevos gastos operativos.
    """
    
    # Lo modificamos para que el 'queryset' sea dinámico
    # si quisiéramos, pero por ahora .all() está bien.
    categoria = forms.ModelChoiceField(
        queryset=CategoriaGasto.objects.all(),
        label="Categoría",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Seleccione una categoría" # Añadimos un 'placeholder'
    )
    
    fecha_imputacion = forms.DateField(
        label="Fecha del Gasto",
        initial=timezone.now().date(),
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = Gasto
        fields = ['categoria', 'monto', 'descripcion', 'fecha_imputacion']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '0.00'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Ej: Factura de luz, período Octubre'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].widget.attrs.update({'class': 'form-select'})