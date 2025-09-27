# applications/pedidos/admin.py

from django.contrib import admin
from .models import Pedido, DetallePedido

class DetallePedidoInline(admin.TabularInline):
    """
    Clase para mostrar los detalles del pedido en formato de tabla
    directamente en la vista del Pedido.
    """
    model = DetallePedido
    extra = 1

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Configuración para el modelo Pedido en el admin."""
    list_display = ('id', 'fecha_hora_pedido', 'cliente', 'estado', 'total_estimado')
    list_filter = ('estado', 'fecha_hora_pedido')
    search_fields = ('id', 'cliente__usuario__nombre_completo')
    
    # Conectamos los detalles del pedido.
    inlines = [DetallePedidoInline]