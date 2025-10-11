# applications/stock/forms.py
from django import forms
from django_select2.forms import Select2Widget
from .models import Producto, Categoria, Marca, Lote, UnidadMedida
from django.utils import timezone
from django.core.exceptions import ValidationError

class ProductoForm(forms.ModelForm):
    # Definimos los campos aquí para personalizar sus querysets y widgets
    busqueda_producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        widget=Select2Widget,
        label="Buscar Producto Existente",
        required=False,
        help_text="Busca un producto para ver si ya existe antes de crear uno nuevo."
    )

    class Meta:
        model = Producto
        # Ahora incluimos todos los campos en 'fields'
        fields = [
            'nombre',
            'descripcion',
            'categoria',
            'marca',
            'unidad_medida',
            'precio_venta',
            'stock_minimo',
            'codigo_barras',
            'es_visible_online',
        ]
        # En 'widgets' van los widgets para TODOS los campos
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': Select2Widget,
            'marca': Select2Widget,
            'unidad_medida': Select2Widget,
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'es_visible_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def clean_precio_venta(self):
        precio_venta = self.cleaned_data.get('precio_venta')
        if precio_venta is not None and precio_venta <= 0:
            raise ValidationError("El precio de venta debe ser un valor mayor que cero.")
        return precio_venta

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'es_visible_online']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'es_visible_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LoteForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(is_active=True),
        widget=Select2Widget
    )
    class Meta:
        model = Lote
        fields = ['producto', 'cantidad_actual', 'precio_compra' ,'fecha_vencimiento']
        widgets = {
            # --- CAMBIO CLAVE ---
            'producto': Select2Widget,
            # --- FIN DEL CAMBIO ---
            'cantidad_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    def clean_fecha_vencimiento(self):
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        
        # Si hay una fecha de vencimiento y es anterior a hoy, lanzamos un error.
        if fecha_vencimiento and fecha_vencimiento < timezone.now().date():
            raise ValidationError("La fecha de vencimiento no puede ser una fecha pasada.")
            
        return fecha_vencimiento
    
    def clean_cantidad_actual(self):
        cantidad = self.cleaned_data.get('cantidad_actual')
        if cantidad is not None and cantidad <= 0:
            raise ValidationError("La cantidad debe ser un número mayor que cero.")
        return cantidad
    
class UploadFileForm(forms.Form):
    file = forms.FileField(label="Selecciona tu archivo Excel (.xlsx)")