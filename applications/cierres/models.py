# applications/cierres/models.py

from django.db import models
from django.conf import settings # Para referenciar nuestro modelo Usuario

class CierreCaja(models.Model):
    fecha_hora_cierre = models.DateTimeField(auto_now_add=True)
    total_calculado = models.DecimalField(max_digits=10, decimal_places=2)
    total_efectivo_real = models.DecimalField(max_digits=10, decimal_places=2)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_tickets = models.PositiveIntegerField()
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'
        ordering = ['-fecha_hora_cierre']

    def __str__(self):
        return f'Cierre del {self.fecha_hora_cierre.strftime("%d/%m/%Y")} por {self.responsable.nombre_completo}'