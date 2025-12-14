# applications/ventas/models.py

"""
Módulo de Modelos para la aplicación de Ventas.

Este archivo define la estructura de datos para gestionar el proceso comercial.
Incluye modelos para registrar los métodos de pago, las cabeceras de las ventas (tickets)
y el detalle de los productos vendidos en cada transacción.
"""

from django.db import models
from django.conf import settings # Para referenciar nuestro modelo Usuario
from applications.usuarios.models import Cliente
from applications.stock.models import Producto

# --- NUEVO MODELO ---
class MetodoPago(models.Model):
    """
    Modelo para gestionar los métodos de pago de forma dinámica.
    
    Permite al administrador configurar qué formas de pago acepta el comercio
    (ej. Efectivo, Tarjeta de Débito, Transferencia, QR), facilitando
    la escalabilidad sin modificar el código fuente.
    """
    nombre = models.CharField('Nombre del Método de Pago', max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

# --- MODELO VENTA MODIFICADO ---
class Venta(models.Model):
    """
    Representa la cabecera de una transacción de venta (Ticket).
    
    Almacena la información general de la operación, como la fecha, el total,
    quién realizó la venta, el cliente asociado y el método de pago utilizado.
    También mantiene la relación con el cierre de caja correspondiente.
    """
    fecha_hora = models.DateTimeField('Fecha y Hora', auto_now_add=True)
    descuento = models.DecimalField('Descuento Aplicado', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    
    # Relación con el método de pago. Si se borra el método, se mantiene el registro en la venta (SET_NULL)
    # para preservar el historial, aunque el método ya no esté disponible para nuevas ventas.
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, verbose_name='Método de Pago')
    
    # Usuario del sistema que registró la venta.
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ventas')
    
    # Cliente asociado a la venta (opcional).
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras')

    # Relación con el cierre de caja. Permite agrupar las ventas por turno o jornada.
    cierre = models.ForeignKey(
        'cierres.CierreCaja',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ventas_incluidas'
    )
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'Venta #{self.id} - {self.fecha_hora.strftime("%d/%m/%Y")}'

# --- MODELO DETALLEVENTA MODIFICADO ---
class DetalleVenta(models.Model):
    """
    Representa cada línea o ítem dentro de una venta.
    
    Vincula un producto específico con la venta general, registrando la cantidad,
    el precio al momento de la transacción y el costo histórico. Esto es vital
    para reportes de rentabilidad precisos, ya que los precios de los productos pueden cambiar.
    """
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    
    # Si se elimina un producto del catálogo, el registro de venta histórica permanece (SET_NULL).
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    
    # Cantidad vendida. Se usan 3 decimales para soportar ventas a granel (ej. 1.500 kg).
    cantidad = models.DecimalField('Cantidad', max_digits=10, decimal_places=3) 
    
    # Precio al que se vendió el producto en ese instante (snapshot).
    precio_unitario_momento = models.DecimalField('Precio Unitario en el Momento', max_digits=10, decimal_places=2)
    
    # Costo del producto en el momento de la venta (calculado vía FEFO/Promedio).
    # Fundamental para calcular la ganancia real de esta transacción específica.
    precio_compra_momento = models.DecimalField('Precio de Compra en el Momento', max_digits=10, decimal_places=2)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para calcular automáticamente el subtotal
        antes de persistir el objeto en la base de datos.
        """
        # Calculamos el subtotal automáticamente antes de guardar
        self.subtotal = self.cantidad * self.precio_unitario_momento
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre if self.producto else "Producto Eliminado"}'