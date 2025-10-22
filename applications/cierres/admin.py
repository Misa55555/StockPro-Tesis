# applications/cierres/admin.py

from django.contrib import admin
from .models import CierreCaja, DetalleCierre

class DetalleCierreInline(admin.TabularInline):
    """
    Permite ver los detalles (por método de pago) directamente 
    en la vista del Cierre de Caja principal.
    """
    model = DetalleCierre
    extra = 0 # No mostrar formularios extra por defecto.
    readonly_fields = ('metodo_pago', 'monto_sistema', 'monto_arqueo', 'diferencia') # Campos de solo lectura
    can_delete = False # No permitir borrar detalles

    def has_add_permission(self, request, obj=None):
        return False # No permitir añadir detalles manualmente

@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    """Configuración para el modelo CierreCaja en el admin."""
    list_display = ('id', 'fecha_cierre', 'usuario', 'total_sistema', 'total_arqueo', 'diferencia')
    list_filter = ('fecha_cierre', 'usuario')
    search_fields = ('id', 'usuario__username')
    readonly_fields = ('fecha_cierre', 'usuario', 'total_sistema', 'total_arqueo', 'diferencia') # Solo lectura
    
    inlines = [DetalleCierreInline] # Incluimos los detalles

    def has_add_permission(self, request):
        return False # Los cierres solo se crean desde la vista específica.

    def has_delete_permission(self, request, obj=None):
        # Permitir borrar solo si no hay ventas asociadas (o decidir tu política)
        # Por seguridad, podríamos deshabilitarlo por completo:
        return False