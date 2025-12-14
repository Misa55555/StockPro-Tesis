# applications/ventas/admin.py

"""
Módulo de administración para la aplicación de Ventas.

Este módulo configura la interfaz administrativa de Django para gestionar las entidades
relacionadas con el proceso de venta: Venta, DetalleVenta y MetodoPago.
Se implementan restricciones de permisos para garantizar la integridad de los datos
financieros, limitando la modificación y eliminación de registros históricos.
"""

from django.contrib import admin
from .models import Venta, DetalleVenta, MetodoPago

class DetalleVentaInline(admin.TabularInline):
    """
    Configuración de la vista en línea para los detalles de venta.
    
    Permite visualizar los productos asociados a una venta específica (relación Maestro-Detalle)
    directamente desde la ficha de la venta principal. Se configura en modo de solo lectura
    para preservar la integridad del registro histórico de la transacción.
    """
    model = DetalleVenta
    extra = 0  # Se deshabilita la generación de formularios vacíos adicionales para nuevos registros.
    
    # Se definen los campos como de solo lectura para evitar alteraciones posteriores a la venta.
    # Esto asegura que los precios y cantidades registrados reflejen exactamente el momento de la transacción.
    readonly_fields = (
        'producto', 
        'cantidad', 
        'precio_unitario_momento', 
        'precio_compra_momento', 
        'subtotal'
    )
    
    can_delete = False  # Se deshabilita la eliminación de líneas de detalle para mantener la consistencia del total.

    def has_add_permission(self, request, obj=None):
        """
        Restringe la adición de nuevos detalles a una venta existente desde el admin.
        
        Args:
            request: La solicitud HTTP actual.
            obj: El objeto venta actual (si existe).
            
        Returns:
            bool: False, impidiendo siempre la adición manual de ítems fuera del flujo del POS.
        """
        return False

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Venta.
    
    Provee una vista completa del historial de transacciones. Se aplican restricciones estrictas
    de permisos (solo lectura y prohibición de borrado) para asegurar que la información
    de ventas permanezca inalterable y auditable.
    """
    # Campos que se mostrarán en la lista general de ventas para una identificación rápida.
    list_display = ('id', 'fecha_hora', 'vendedor', 'cliente', 'metodo_pago', 'total')
    
    # Filtros laterales para facilitar la búsqueda y segmentación de ventas por fecha, método o vendedor.
    list_filter = ('fecha_hora', 'metodo_pago', 'vendedor')
    
    # Configuración de búsqueda: permite buscar por ID de venta, nombre del cliente o usuario del vendedor.
    # Se utiliza la notación de doble guion bajo (__) para acceder a campos de modelos relacionados.
    search_fields = ('id', 'cliente__usuario__nombre_completo', 'vendedor__username')
    
    # Todos los campos principales de la venta se marcan como solo lectura.
    readonly_fields = ('fecha_hora', 'vendedor', 'cliente', 'metodo_pago', 'total')
    
    # Integración de la vista inline de detalles para ver los productos vendidos dentro de la misma pantalla.
    inlines = [DetalleVentaInline]

    def has_add_permission(self, request):
        """
        Deshabilita la creación manual de ventas desde el panel de administración.
        
        Las ventas deben generarse exclusivamente a través de la interfaz del Punto de Venta (POS)
        para garantizar la correcta ejecución de la lógica de negocio (descuento de stock, cálculos, etc.).
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Deshabilita la eliminación de ventas desde el panel de administración.
        
        Esta medida de seguridad previene la pérdida accidental o malintencionada de registros
        financieros y de auditoría.
        """
        return False

# --- REGISTRO DEL NUEVO MODELO ---
@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo MetodoPago.
    
    Permite la gestión (creación, edición y listado) de los métodos de pago aceptados en el sistema.
    """
    list_display = ('nombre', 'is_active')
    
    # Permite activar o desactivar métodos de pago directamente desde la vista de lista,
    # agilizando la gestión operativa.
    list_editable = ('is_active',)
    
    search_fields = ('nombre',)