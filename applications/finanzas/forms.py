# applications/finanzas/forms.py

"""
Módulo de Formularios para la aplicación 'finanzas'.

Este archivo define los formularios basados en modelos (ModelForms) necesarios para la
interacción con el módulo financiero. Incluye la estructura para el registro de
nuevos gastos operativos y la gestión dinámica de categorías de gastos, integrando
widgets personalizados para mejorar la experiencia de usuario en el frontend.
"""

from django import forms
from .models import Gasto, CategoriaGasto
from django.utils import timezone

# --- Formulario para la Categoría ---
class CategoriaGastoForm(forms.ModelForm):
    """
    Formulario para la creación y edición de Categorías de Gastos.

    Diseñado para ser utilizado en interfaces modales, permite la definición ágil
    de nuevos conceptos de agrupación para los egresos (ej. 'Logística', 'Mantenimiento').
    """
    class Meta:
        """Metadatos de configuración del formulario CategoriaGastoForm."""
        model = CategoriaGasto
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Alquiler, Servicios, Sueldos'
            })
        }

# --- Formulario de Gasto ---
class GastoForm(forms.ModelForm):
    """
    Formulario principal para el registro de Gastos Operativos.

    Permite a los usuarios autorizados ingresar los detalles de un egreso,
    asociándolo a una categoría existente y definiendo su fecha de imputación contable.
    """
    
    # Campo de selección para la categoría del gasto.
    # Se utiliza un ModelChoiceField para garantizar que la selección corresponda a una entidad válida.
    categoria = forms.ModelChoiceField(
        queryset=CategoriaGasto.objects.all(),
        label="Categoría",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Seleccione una categoría" # Placeholder para el selector.
    )
    
    # Campo para la fecha de imputación del gasto.
    # Se inicializa con la fecha actual del sistema para agilizar la carga.
    fecha_imputacion = forms.DateField(
        label="Fecha del Gasto",
        initial=timezone.now().date(),
        widget=forms.DateInput(
            attrs={
                'type': 'date', # Activa el selector de fecha nativo del navegador.
                'class': 'form-control'
            }
        )
    )

    class Meta:
        """Metadatos de configuración del formulario GastoForm."""
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
        """
        Inicializador del formulario.
        
        Permite la personalización dinámica de los atributos de los campos al momento de instanciar la clase.
        En este caso, asegura que el widget del campo 'categoria' tenga la clase CSS correcta.
        """
        super().__init__(*args, **kwargs)
        self.fields['categoria'].widget.attrs.update({'class': 'form-select'})