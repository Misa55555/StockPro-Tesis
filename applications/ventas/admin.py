# applications/ventas/admin.py

from django.contrib import admin
from .models import Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    """
    Clase para mostrar los detalles de la venta en formato de tabla
    directamente en la vista de la Venta.
    """
    model = DetalleVenta
    extra = 1  # Número de líneas extra para añadir productos.

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    """Configuración para el modelo Venta en el admin."""
    list_display = ('id', 'fecha_hora', 'vendedor', 'cliente', 'total', 'metodo_pago')
    list_filter = ('fecha_hora', 'metodo_pago', 'vendedor')
    search_fields = ('id', 'cliente__usuario__nombre_completo', 'vendedor__nombre_completo')
    
    # Aquí conectamos los detalles para que se puedan editar en la misma página.
    inlines = [DetalleVentaInline]