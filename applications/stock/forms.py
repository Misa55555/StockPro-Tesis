# applications/stock/forms.py
from django import forms
from django_select2.forms import Select2Widget
from .models import Producto, Categoria, Marca, Lote, UnidadMedida

class ProductoForm(forms.ModelForm):
    # Campo extra para la búsqueda de productos existentes, no se guarda en la BD.
    busqueda_producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        widget=Select2Widget,
        label="Buscar Producto Existente",
        required=False,
        help_text="Busca un producto para ver si ya existe antes de crear uno nuevo."
    )

    class Meta:
        model = Producto
        fields = [
            # 'busqueda_producto' no se incluye aquí porque no es parte del modelo.
            'nombre',
            'categoria',
            'marca',
            'unidad_medida',
            'descripcion',
            'precio_compra',
            'precio_venta',
            'stock_minimo',
            'codigo_barras',
            'es_visible_online',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            # --- INICIO DE LOS CAMBIOS ---
            'categoria': Select2Widget,
            'marca': Select2Widget,
            'unidad_medida': Select2Widget,
            # --- FIN DE LOS CAMBIOS ---
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'es_visible_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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
    class Meta:
        model = Lote
        fields = ['producto', 'cantidad_actual', 'fecha_vencimiento']
        widgets = {
            # --- CAMBIO CLAVE ---
            'producto': Select2Widget,
            # --- FIN DEL CAMBIO ---
            'cantidad_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Selecciona tu archivo Excel (.xlsx)")