# applications/stock/models.py

from django.db import models
from django.db.models import Sum

class Marca(models.Model):
    nombre = models.CharField('Nombre de la Marca', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class UnidadMedida(models.Model):
    nombre = models.CharField('Unidad de Medida', max_length=50, unique=True)
    abreviatura = models.CharField('Abreviatura', max_length=10)

    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    es_visible_online = models.BooleanField('Visible en portal cliente', default=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    precio_compra = models.DecimalField('Precio de Compra', max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField('Precio de Venta', max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField('Stock Mínimo de Alerta', max_digits=10, decimal_places=3, default=5.000)
    es_visible_online = models.BooleanField('Visible en portal cliente', default=True)
    codigo_barras = models.CharField('Código de Barras', max_length=100, blank=True, null=True, unique=True)

    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def get_stock_total(self):
        """Calcula el stock total sumando las cantidades de todos los lotes."""
        total = self.lotes.aggregate(total_stock=Sum('cantidad_actual'))['total_stock']
        return total if total is not None else 0
    
    def __str__(self):
        return self.nombre

class Lote(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    cantidad_actual = models.DecimalField('Cantidad Actual', max_digits=10, decimal_places=3)
    fecha_vencimiento = models.DateField('Fecha de Vencimiento', null=True, blank=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['fecha_vencimiento']

    def __str__(self):
        return f'Lote de {self.producto.nombre} - Vence: {self.fecha_vencimiento}'