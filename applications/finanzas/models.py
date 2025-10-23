# applications/finanzas/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class CategoriaGasto(models.Model):
    """
    Agrupa los gastos en categorías (ej. Servicios, Alquiler, Sueldos, Marketing).
    
    Esto es fundamental para el dashboard, para poder filtrar y ver
    en qué se está gastando el dinero.
    """
    nombre = models.CharField('Nombre de la Categoría', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Categoría de Gasto'
        verbose_name_plural = 'Categorías de Gastos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Gasto(models.Model):
    """
    Representa un gasto operativo individual del negocio.
    
    Este modelo registrará cada salida de dinero que no sea
    la compra de mercadería (ej. la factura de luz, el alquiler del mes).
    """
    categoria = models.ForeignKey(
        CategoriaGasto, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Categoría'
    )
    usuario_registra = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Usuario que registra'
    )
    monto = models.DecimalField('Monto', max_digits=12, decimal_places=2)
    descripcion = models.TextField('Descripción', blank=True)
    
    # --- ESTE ES EL CAMPO CLAVE ---
    # Responde a tu duda sobre los gastos mensuales.
    fecha_imputacion = models.DateField(
        'Fecha de Imputación',
        default=timezone.now,
        help_text="La fecha a la que pertenece el gasto (ej. la factura de luz de Septiembre, se imputa en Septiembre, aunque se pague en Octubre)."
    )
    
    fecha_registro = models.DateTimeField('Fecha de Registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-fecha_imputacion']

    def __str__(self):
        return f"Gasto: ${self.monto} - {self.categoria.nombre} ({self.fecha_imputacion.strftime('%d/%m/%Y')})"