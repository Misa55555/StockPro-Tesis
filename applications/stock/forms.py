# applications/stock/forms.py

"""
Módulo de Formularios para la aplicación 'stock'.

Este archivo contiene la definición de los formularios utilizados para la gestión
del inventario. Incluye formularios basados en modelos (ModelForms) para la creación
y edición de Productos, Categorías, Marcas y Lotes, así como formularios estándar
para operaciones de gestión masiva (actualización de precios).
Se integran validaciones personalizadas y widgets avanzados (Select2) para mejorar
la usabilidad y la integridad de los datos.
"""

from django import forms
from django_select2.forms import Select2Widget
from .models import Producto, Categoria, Marca, Lote, UnidadMedida
from django.utils import timezone
from django.core.exceptions import ValidationError

class ProductoForm(forms.ModelForm):
    """
    Formulario para la creación y edición de Productos.

    Este formulario gestiona la información comercial y de clasificación del producto.
    Incorpora un campo auxiliar de búsqueda para evitar la duplicación de registros
    antes de la creación.
    """
    
    # Campo auxiliar no persistente en BD, utilizado en la interfaz para verificar existencia previa.
    busqueda_producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        widget=Select2Widget,
        label="Buscar Producto Existente",
        required=False,
        help_text="Busca un producto para ver si ya existe antes de crear uno nuevo."
    )

    class Meta:
        """Metadatos de configuración del formulario ProductoForm."""
        model = Producto
        # Definición explícita de campos para garantizar el orden y la seguridad.
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
        # Configuración de widgets para estilizado con Bootstrap y funcionalidad avanzada.
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': Select2Widget, # Widget con buscador integrado para claves foráneas.
            'marca': Select2Widget,
            'unidad_medida': Select2Widget,
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'es_visible_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_precio_venta(self):
        """
        Validación personalizada para el campo 'precio_venta'.
        
        Asegura que el precio de venta al público sea un valor positivo.
        
        Returns:
            Decimal: El precio validado.
            
        Raises:
            ValidationError: Si el precio es menor o igual a cero.
        """
        precio_venta = self.cleaned_data.get('precio_venta')
        if precio_venta is not None and precio_venta <= 0:
            raise ValidationError("El precio de venta debe ser un valor mayor que cero.")
        return precio_venta

class CategoriaForm(forms.ModelForm):
    """
    Formulario para la gestión de Categorías de productos.
    """
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MarcaForm(forms.ModelForm):
    """
    Formulario para la gestión de Marcas comerciales.
    """
    class Meta:
        model = Marca
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LoteForm(forms.ModelForm):
    """
    Formulario para el registro de nuevos Lotes de inventario (Ingreso de Mercadería).

    Este formulario es complejo ya que no solo maneja la creación del objeto Lote,
    sino que incluye campos auxiliares para facilitar cálculos matemáticos (costo total vs unitario)
    y la actualización opcional del precio de venta del producto padre.
    """
    
    # Selector de producto filtrado solo a productos activos.
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(is_active=True),
        widget=Select2Widget(attrs={'class': 'form-control', 'id': 'id_producto_select'}) # ID específico para manipulación vía JS.
    )
    
    # Campo auxiliar para calcular el costo unitario a partir del total de la factura.
    costo_total_compra = forms.DecimalField(
        label="Costo Total de la Factura",
        required=False,
        max_digits=12, decimal_places=2,
        help_text="Ingresa el total pagado por esta cantidad de productos para calcular el costo unitario automáticamente.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_costo_total'})
    )

    # Checkbox para permitir actualizar el precio de venta del producto base tras la carga del lote.
    actualizar_precio = forms.BooleanField(
        label="¿Actualizar Precio de Venta del Producto?",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_check_precio'})
    )
    
    # Campo para definir el nuevo precio de venta si se activó la opción anterior.
    nuevo_precio_venta = forms.DecimalField(
        label="Nuevo Precio de Venta",
        required=False,
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_nuevo_precio', 'readonly': True})
    )
    

    class Meta:
        """Metadatos del formulario LoteForm."""
        model = Lote
        fields = ['producto', 'cantidad_actual', 'precio_compra', 'fecha_vencimiento']
        widgets = {
            # Asignación de IDs específicos para facilitar la lógica de cálculo en el frontend (JavaScript).
            'cantidad_actual': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_cantidad'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_precio_compra_unitario'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'cantidad_actual': 'Cantidad Recibida',
            'precio_compra': 'Costo Unitario (Calculado)',
        }

    def clean_fecha_vencimiento(self):
        """
        Validación de la fecha de vencimiento.
        
        Impide el ingreso de lotes con fechas de vencimiento pasadas.
        """
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        
        if fecha_vencimiento and fecha_vencimiento < timezone.now().date():
            raise ValidationError("La fecha de vencimiento no puede ser una fecha pasada.")
            
        return fecha_vencimiento
    
    def clean_cantidad_actual(self):
        """
        Validación de la cantidad ingresada.
        
        Asegura que el stock ingresado sea estrictamente positivo.
        """
        cantidad = self.cleaned_data.get('cantidad_actual')
        if cantidad is not None and cantidad <= 0:
            raise ValidationError("La cantidad debe ser un número mayor que cero.")
        return cantidad
    
class ActualizarPrecioMarcaForm(forms.Form):
    """
    Formulario para la actualización masiva de precios por Marca.

    Permite aplicar un ajuste porcentual (aumento o descuento) a todos los productos
    asociados a una marca específica. No está vinculado directamente a un modelo.
    """
    porcentaje = forms.DecimalField(
        label="Porcentaje de Ajuste (%)",
        max_digits=5, 
        decimal_places=2,
        help_text="Ingresa un valor positivo para aumentar (ej. 15) o negativo para descontar (ej. -10).",
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ej: 10.5',
            'step': '0.01'
        })
    )