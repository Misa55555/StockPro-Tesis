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
        widget=Select2Widget(attrs={'class': 'form-control', 'id': 'id_producto_select'}) # Añadimos ID para JS
    )
    
   
    costo_total_compra = forms.DecimalField(
        label="Costo Total de la Factura",
        required=False,
        max_digits=12, decimal_places=2,
        help_text="Ingresa el total pagado por esta cantidad de productos para calcular el costo unitario automáticamente.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_costo_total'})
    )

    actualizar_precio = forms.BooleanField(
        label="¿Actualizar Precio de Venta del Producto?",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_check_precio'})
    )
    
    nuevo_precio_venta = forms.DecimalField(
        label="Nuevo Precio de Venta",
        required=False,
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_nuevo_precio', 'readonly': True})
    )
    

    class Meta:
        model = Lote
        fields = ['producto', 'cantidad_actual', 'precio_compra', 'fecha_vencimiento']
        widgets = {
            # Añadimos IDs específicos para facilitar el JavaScript
            'cantidad_actual': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_cantidad'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_precio_compra_unitario'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'cantidad_actual': 'Cantidad Recibida',
            'precio_compra': 'Costo Unitario (Calculado)',
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
    
