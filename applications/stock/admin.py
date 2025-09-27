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
    model = Lote
    extra = 1
    # --- INICIO DE LA CORRECCIÓN ---
    # Usamos los nombres de campo que existen en el modelo Lote
    fields = ('cantidad_actual', 'fecha_vencimiento')
    # --- FIN DE LA CORRECCIÓN ---

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'categoria',
        'marca',
        'precio_venta',
        'stock_total',
        'stock_minimo',
    )
    list_filter = ('categoria', 'marca')
    search_fields = ('nombre', 'codigo_barras')
    ordering = ('nombre',)
    
    inlines = [LoteInline]
    
    def stock_total(self, obj):
        return obj.get_stock_total()
    stock_total.short_description = 'Stock Total (Calculado)'