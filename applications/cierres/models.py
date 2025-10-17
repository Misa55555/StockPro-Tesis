# applications/cierres/models.py
from django.db import models
from django.conf import settings
from applications.ventas.models import Venta, MetodoPago

class CierreCaja(models.Model):
    """
    Representa el evento de cierre de caja al final de un turno o día.
    """
    fecha_cierre = models.DateTimeField('Fecha y Hora de Cierre', auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='Usuario que cierra'
    )
    
    # Totales generales
    total_sistema = models.DecimalField('Total Calculado por Sistema', max_digits=12, decimal_places=2, default=0)
    total_arqueo = models.DecimalField('Total Contado (Arqueo)', max_digits=12, decimal_places=2, default=0)
    diferencia = models.DecimalField('Diferencia', max_digits=12, decimal_places=2, default=0)
    
    observaciones = models.TextField('Observaciones', blank=True, null=True)

    class Meta:
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'
        ordering = ['-fecha_cierre']

    def __str__(self):
        return f"Cierre #{self.id} - {self.fecha_cierre.strftime('%d/%m/%Y %H:%M')}"


class DetalleCierre(models.Model):
    """
    Guarda el desglose de un cierre de caja por cada método de pago.
    """
    cierre = models.ForeignKey(CierreCaja, on_delete=models.CASCADE, related_name='detalles')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, verbose_name='Método de Pago')
    
    monto_sistema = models.DecimalField('Monto Sistema', max_digits=10, decimal_places=2)
    monto_arqueo = models.DecimalField('Monto Contado', max_digits=10, decimal_places=2)
    
    @property
    def diferencia(self):
        return self.monto_arqueo - self.monto_sistema

    class Meta:
        verbose_name = 'Detalle de Cierre'
        verbose_name_plural = 'Detalles de Cierre'
        unique_together = ('cierre', 'metodo_pago') # Evita duplicados

    def __str__(self):
        return f"{self.metodo_pago.nombre}: ${self.monto_arqueo}"