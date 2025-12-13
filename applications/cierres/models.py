# applications/cierres/models.py

"""
Módulo de Modelos para la aplicación 'cierres'.

Este archivo define las estructuras de datos fundamentales para el registro y control
de los cierres de caja. Los modelos aquí descritos permiten la persistencia de la
información financiera al finalizar los turnos, facilitando la auditoría de los ingresos
mediante la comparación entre los valores calculados por el sistema y los valores
físicos reportados (arqueo).
"""

from django.db import models
from django.conf import settings
from applications.ventas.models import Venta, MetodoPago

class CierreCaja(models.Model):
    """
    Entidad que representa el evento de consolidación y cierre de caja.

    Este modelo actúa como el registro maestro de una operación de cierre, almacenando
    los totales generales, la identificación del responsable y las discrepancias detectadas.
    Sirve como punto de agrupación para los detalles desglosados por método de pago.
    """
    # Fecha y hora exacta en que se procesó el cierre.
    fecha_cierre = models.DateTimeField('Fecha y Hora de Cierre', auto_now_add=True)
    
    # Usuario responsable de ejecutar la operación de cierre.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='Usuario que cierra'
    )
    
    # Totales monetarios generales para auditoría rápida.
    total_sistema = models.DecimalField('Total Calculado por Sistema', max_digits=12, decimal_places=2, default=0)
    total_arqueo = models.DecimalField('Total Contado (Arqueo)', max_digits=12, decimal_places=2, default=0)
    diferencia = models.DecimalField('Diferencia', max_digits=12, decimal_places=2, default=0)
    
    # Campo para notas adicionales o justificaciones sobre diferencias.
    observaciones = models.TextField('Observaciones', blank=True, null=True)

    class Meta:
        """Metadatos para la configuración del modelo CierreCaja."""
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'
        ordering = ['-fecha_cierre'] # Orden descendente para mostrar primero los cierres más recientes.

    def __str__(self):
        """Retorna una representación legible del objeto CierreCaja."""
        return f"Cierre #{self.id} - {self.fecha_cierre.strftime('%d/%m/%Y %H:%M')}"


class DetalleCierre(models.Model):
    """
    Entidad que almacena el detalle financiero por método de pago para un cierre específico.

    Permite descomponer el cierre general en sus partes constituyentes (ej. efectivo, tarjetas),
    facilitando la identificación precisa del origen de cualquier discrepancia financiera.
    """
    # Relación con el cierre maestro. Si se borra el cierre, se borran sus detalles.
    cierre = models.ForeignKey(CierreCaja, on_delete=models.CASCADE, related_name='detalles')
    
    # Método de pago asociado a este detalle (Efectivo, Débito, etc.).
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, verbose_name='Método de Pago')
    
    # Valores monetarios específicos para este método de pago.
    monto_sistema = models.DecimalField('Monto Sistema', max_digits=10, decimal_places=2)
    monto_arqueo = models.DecimalField('Monto Contado', max_digits=10, decimal_places=2)
    
    @property
    def diferencia(self):
        """
        Propiedad calculada que retorna la diferencia monetaria para este método de pago.
        
        Returns:
            Decimal: La resta entre el monto contado (arqueo) y el monto registrado por el sistema.
        """
        return self.monto_arqueo - self.monto_sistema

    class Meta:
        """Metadatos para el modelo DetalleCierre."""
        verbose_name = 'Detalle de Cierre'
        verbose_name_plural = 'Detalles de Cierre'
        # Restricción de unicidad: no puede haber dos detalles para el mismo método de pago en un mismo cierre.
        unique_together = ('cierre', 'metodo_pago') 

    def __str__(self):
        """Representación en cadena del detalle de cierre."""
        return f"{self.metodo_pago.nombre}: ${self.monto_arqueo}"