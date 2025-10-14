# applications/ventas/admin.py

from django.contrib import admin
from .models import Venta, DetalleVenta, MetodoPago # Importamos todos los modelos

class DetalleVentaInline(admin.TabularInline):
    """
    Permite ver y editar los productos de una venta directamente 
    desde la página de la Venta.
    """
    model = DetalleVenta
    extra = 0 # No mostrar formularios extra por defecto.
    readonly_fields = ('producto', 'cantidad', 'precio_unitario_momento', 'precio_compra_momento', 'subtotal') # Hacemos los campos de solo lectura una vez creados.
    can_delete = False # Evitamos que se borren detalles de una venta ya registrada.

    def has_add_permission(self, request, obj=None):
        return False # No permitir añadir nuevos detalles desde el admin.

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    """Configuración para el modelo Venta en el admin."""
    list_display = ('id', 'fecha_hora', 'vendedor', 'cliente', 'metodo_pago', 'total')
    list_filter = ('fecha_hora', 'metodo_pago', 'vendedor')
    search_fields = ('id', 'cliente__usuario__nombre_completo', 'vendedor__username')
    readonly_fields = ('fecha_hora', 'vendedor', 'cliente', 'metodo_pago', 'total') # Las ventas no se deberían modificar desde el admin.
    
    inlines = [DetalleVentaInline]

    def has_add_permission(self, request):
        return False # Las ventas solo se deben crear desde el POS.

    def has_delete_permission(self, request, obj=None):
        return False # Por seguridad, no permitir borrar ventas desde el admin.

# --- REGISTRO DEL NUEVO MODELO ---
@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    """Configuración para el modelo MetodoPago en el admin."""
    list_display = ('nombre', 'is_active')
    list_editable = ('is_active',) # Permite editar el estado directamente desde la lista.
    search_fields = ('nombre',)