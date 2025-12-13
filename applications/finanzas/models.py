# applications/finanzas/models.py

"""
Módulo de Modelos para la aplicación 'finanzas'.

Este archivo define las estructuras de datos necesarias para la gestión de los egresos
operativos del negocio. Permite la clasificación y registro de gastos que no corresponden
al costo de mercadería vendida (COGS), tales como servicios, alquileres o sueldos,
facilitando así el análisis de rentabilidad neta y el control presupuestario.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone

class CategoriaGasto(models.Model):
    """
    Entidad que clasifica los gastos operativos en grupos lógicos.

    Permite organizar los egresos en categorías (ej. 'Infraestructura', 'Personal', 'Marketing')
    para su posterior análisis en el dashboard financiero. Esta clasificación es esencial
    para identificar los centros de costos más relevantes.
    """
    # Nombre único identificador de la categoría.
    nombre = models.CharField('Nombre de la Categoría', max_length=100, unique=True)

    class Meta:
        """Metadatos para la configuración del modelo CategoriaGasto."""
        verbose_name = 'Categoría de Gasto'
        verbose_name_plural = 'Categorías de Gastos'
        ordering = ['nombre'] # Orden alfabético para facilitar la búsqueda en selectores.

    def __str__(self):
        """Retorna el nombre de la categoría como representación del objeto."""
        return self.nombre

class Gasto(models.Model):
    """
    Entidad que representa un egreso monetario operativo individual.

    Este modelo registra las salidas de dinero no vinculadas directamente a la adquisición
    de stock (compras de mercadería), permitiendo diferenciar entre costos directos y
    gastos operativos. Incluye la fecha de imputación para asegurar que el gasto impacte
    en el período contable correcto, independientemente de la fecha de registro.
    """
    # Clasificación del gasto. Si se elimina la categoría, el gasto persiste (SET_NULL) para mantener el histórico.
    categoria = models.ForeignKey(
        CategoriaGasto, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Categoría'
    )
    
    # Usuario que auditó o registró el gasto en el sistema.
    usuario_registra = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Usuario que registra'
    )
    
    # Importe monetario del gasto.
    monto = models.DecimalField('Monto', max_digits=12, decimal_places=2)
    
    # Detalle descriptivo o justificación del egreso.
    descripcion = models.TextField('Descripción', blank=True)
    
    # Fecha contable a la que corresponde el gasto (Principio de Devengado).
    # Permite asignar gastos a meses anteriores o futuros según corresponda (ej. pagar en Octubre la luz de Septiembre).
    fecha_imputacion = models.DateField(
        'Fecha de Imputación',
        default=timezone.now,
        help_text="La fecha a la que pertenece el gasto (ej. la factura de luz de Septiembre, se imputa en Septiembre, aunque se pague en Octubre)."
    )
    
    # Fecha real de carga en el sistema (Audit trail).
    fecha_registro = models.DateTimeField('Fecha de Registro', auto_now_add=True)

    class Meta:
        """Metadatos para la configuración del modelo Gasto."""
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-fecha_imputacion'] # Orden descendente para priorizar la visualización de gastos recientes.

    def __str__(self):
        """Representación legible del gasto, incluyendo monto, categoría y fecha."""
        return f"Gasto: ${self.monto} - {self.categoria.nombre} ({self.fecha_imputacion.strftime('%d/%m/%Y')})"