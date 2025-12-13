# applications/stock/admin.py

"""
Módulo de configuración del Panel de Administración para la aplicación 'stock'.

Este archivo define la interfaz de gestión para los modelos fundamentales del inventario:
Productos, Categorías, Marcas, Unidades de Medida y Lotes. La configuración se centra
en facilitar la administración del catálogo y el control de existencias, permitiendo
la visualización del stock consolidado y la gestión detallada de lotes directamente
desde la ficha del producto.
"""

from django.contrib import admin
from .models import Categoria, Producto, Marca, UnidadMedida, Lote

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para el modelo Categoria.

    Permite la gestión de las categorías de productos, visualizando su estado de
    visibilidad en el portal online.
    """
    list_display = ('nombre', 'es_visible_online')
    search_fields = ('nombre',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para el modelo Marca.

    Facilita la administración de las marcas comerciales asociadas a los productos.
    """
    search_fields = ('nombre',)

@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para el modelo UnidadMedida.

    Permite definir y estandarizar las unidades de medida (ej. kg, litros, unidades)
    utilizadas para cuantificar el stock y las ventas.
    """
    list_display = ('nombre', 'abreviatura')

class LoteInline(admin.TabularInline):
    """
    Configuración de vista en línea (Inline) para el modelo Lote.

    Permite la gestión (creación, edición, visualización) de los lotes de stock
    directamente dentro de la ficha de administración del Producto. Esto facilita
    la carga de inventario sin necesidad de navegar a una vista separada.
    """
    model = Lote
    extra = 1 # Provee un formulario vacío adicional por defecto para agilizar la carga de nuevos lotes.
    fields = ('cantidad_actual', 'precio_compra', 'fecha_vencimiento')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración principal para la administración del modelo Producto.

    Esta clase personaliza la vista de productos para incluir cálculos dinámicos de stock,
    filtros avanzados y la integración con la gestión de lotes. Es el punto central
    para la administración del catálogo.
    """
    list_display = (
        'nombre',
        'categoria',
        'marca',
        'precio_venta',
        'get_stock_total', # Método calculado para visualizar el stock real disponible.
        'stock_minimo',
    )
    list_filter = ('categoria', 'marca')
    search_fields = ('nombre', 'codigo_barras')
    ordering = ('nombre',)
    
    # Integra la gestión de lotes dentro del formulario del producto.
    inlines = [LoteInline]
    
    def get_stock_total(self, obj):
        """
        Calcula y retorna el stock total consolidado del producto.

        Invoca el método de negocio del modelo para sumar las existencias de todos
        los lotes activos, permitiendo ver el total disponible en la lista de productos.
        
        Args:
            obj: Instancia del producto actual.
            
        Returns:
            Decimal: La suma total de las cantidades actuales de los lotes.
        """
        return obj.get_stock_total()
    get_stock_total.short_description = 'Stock Total (Calculado)'

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para el modelo Lote.

    Provee una vista detallada de todos los lotes de inventario, útil para auditorías,
    control de vencimientos y seguimiento de precios de compra históricos.
    """
    list_display = ('producto', 'cantidad_actual', 'precio_compra', 'fecha_vencimiento')
    list_filter = ('producto__categoria', 'producto__marca')
    search_fields = ('producto__nombre',)