# applications/ventas/models.py

from django.db import models
from django.conf import settings # Para referenciar nuestro modelo Usuario
from applications.usuarios.models import Cliente
from applications.stock.models import Producto

# --- NUEVO MODELO ---
# Modelo para gestionar los métodos de pago de forma dinámica.
class MetodoPago(models.Model):
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
    fecha_hora = models.DateTimeField('Fecha y Hora', auto_now_add=True)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    
    # --- CAMBIO CLAVE: Usamos una ForeignKey al nuevo modelo ---
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, verbose_name='Método de Pago')
    
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ventas')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras')

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'Venta #{self.id} - {self.fecha_hora.strftime("%d/%m/%Y")}'

# --- MODELO DETALLEVENTA MODIFICADO ---
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.DecimalField('Cantidad', max_digits=10, decimal_places=3) # Permitimos decimales para ventas a granel
    precio_unitario_momento = models.DecimalField('Precio Unitario en el Momento', max_digits=10, decimal_places=2)
    
    # --- CAMBIO ACORDADO: Campo para registrar el costo y calcular rentabilidad ---
    precio_compra_momento = models.DecimalField('Precio de Compra en el Momento', max_digits=10, decimal_places=2)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'

    def save(self, *args, **kwargs):
        # Calculamos el subtotal automáticamente antes de guardar
        self.subtotal = self.cantidad * self.precio_unitario_momento
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre if self.producto else "Producto Eliminado"}'