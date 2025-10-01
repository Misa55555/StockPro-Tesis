# applications/stock/admin.py

from django.contrib import admin
from .models import Categoria, Producto, Marca, UnidadMedida, Lote

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'es_visible_online')
    search_fields = ('nombre',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)

@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura')

class LoteInline(admin.TabularInline):
    """Permite añadir y editar lotes directamente desde la página del producto."""
    model = Lote
    extra = 1 # Muestra un campo vacío para añadir un nuevo lote.
    fields = ('cantidad_actual', 'precio_compra', 'fecha_vencimiento')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'categoria',
        'marca',
        'precio_venta',
        'get_stock_total', # Usamos el método para mostrar el stock
        'stock_minimo',
    )
    list_filter = ('categoria', 'marca')
    search_fields = ('nombre', 'codigo_barras')
    ordering = ('nombre',)
    
    # Conectamos los lotes para que se gestionen dentro del producto
    inlines = [LoteInline]
    
    # Campo para mostrar en la lista que no es un campo de BD
    def get_stock_total(self, obj):
        return obj.get_stock_total()
    get_stock_total.short_description = 'Stock Total (Calculado)'

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad_actual', 'precio_compra', 'fecha_vencimiento')
    list_filter = ('producto__categoria', 'producto__marca')
    search_fields = ('producto__nombre',)