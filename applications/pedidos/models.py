# applications/pedidos/models.py

from django.db import models
from applications.usuarios.models import Cliente
from applications.stock.models import Producto

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    fecha_hora_pedido = models.DateTimeField(auto_now_add=True)
    total_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')

    class Meta:
        verbose_name = 'Pedido de Cliente'
        verbose_name_plural = 'Pedidos de Clientes'
        ordering = ['-fecha_hora_pedido']

    def __str__(self):
        return f'Pedido #{self.id} - {self.cliente.usuario.nombre_completo}'

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'