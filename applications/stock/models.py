# applications/stock/models.py

"""
Módulo de Modelos para la aplicación 'stock'.

Este archivo define la estructura de datos para la gestión del inventario del comercio.
Incluye modelos para entidades clave como Producto, Categoría, Marca y Unidad de Medida.
Una de las decisiones de diseño más importantes ha sido la implementación de un sistema
de Lotes para el manejo del stock, lo que permite un control más granular de las
existencias, el seguimiento de fechas de vencimiento y un registro histórico de
los ingresos de mercadería.
"""

from django.db import models
from django.db.models import Sum

class Marca(models.Model):
    """
    Representa la marca comercial de un producto (ej. Coca-Cola, Bimbo, Lays).
    
    Este modelo permite agrupar productos bajo un mismo fabricante o sello comercial,
    facilitando la búsqueda, la generación de reportes segmentados y la gestión
    organizada del inventario.
    """
    # Campo para el nombre único de la marca.
    nombre = models.CharField(
        'Nombre de la Marca',
        max_length=100,
        unique=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        """Metadatos para la configuración del modelo Marca."""
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre'] # Ordena las marcas alfabéticamente para su visualización.

    def __str__(self):
        """Retorna la representación en cadena de texto del objeto Marca."""
        return self.nombre

class UnidadMedida(models.Model):
    """
    Define las unidades de medida estandarizadas para los productos (ej. Unidad, Kilogramo, Litro).
    
    Es un modelo crucial para la correcta gestión del stock, especialmente para productos
    fraccionables, y para estandarizar la cuantificación en los procesos de compra y venta.
    """
    # Nombre completo de la unidad de medida.
    nombre = models.CharField(
        'Unidad de Medida',
        max_length=50,
        unique=True
    )
    # Abreviatura estándar (ej. "un", "kg", "L") para uso en interfaces compactas.
    abreviatura = models.CharField(
        'Abreviatura',
        max_length=10
    )

    class Meta:
        """Metadatos para la configuración del modelo UnidadMedida."""
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['nombre']

    def __str__(self):
        """Retorna la representación en cadena de texto del objeto UnidadMedida."""
        return self.nombre

class Categoria(models.Model):
    """
    Clasificación lógica de los productos (ej. Bebidas, Lácteos, Panificados).
    
    Este modelo es fundamental para la organización jerárquica del inventario y la
    navegación en el catálogo, permitiendo filtrar y localizar productos de manera eficiente.
    """
    # Nombre único identificador de la categoría.
    nombre = models.CharField(
        'Nombre',
        max_length=100,
        unique=True
    )
    # Control de visibilidad para canales digitales o catálogos públicos.
    es_visible_online = models.BooleanField(
        'Visible en portal cliente',
        default=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        """Metadatos para la configuración del modelo Categoria."""
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        """Retorna la representación en cadena de texto del objeto Categoria."""
        return self.nombre

class Producto(models.Model):
    """
    Entidad central del módulo de stock que representa un artículo comercializable.
    
    Este modelo agrupa la información descriptiva, comercial y de clasificación del producto.
    Es importante notar que no almacena el nivel de stock directamente; el stock total
    se deriva dinámicamente de la agregación de los Lotes asociados activos.
    """
    # Atributos descriptivos y comerciales.
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    precio_venta = models.DecimalField('Precio de Venta', max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField('Stock Mínimo de Alerta', max_digits=10, decimal_places=3, default=5.000)
    es_visible_online = models.BooleanField('Visible en portal cliente', default=True)
    is_active = models.BooleanField(default=True)
    codigo_barras = models.CharField('Código de Barras', max_length=100, blank=True, null=True, unique=True)

    # Relaciones de clasificación (Foreign Keys).
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL, # Mantiene el producto aunque se elimine la categoría.
        null=True, blank=True, related_name='productos'
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL, # Mantiene el producto aunque se elimine la marca.
        null=True, blank=True, related_name='productos'
    )
    unidad_medida = models.ForeignKey(
        UnidadMedida,
        on_delete=models.PROTECT # Impide eliminar una unidad de medida si está en uso.
    )

    class Meta:
        """Metadatos para la configuración del modelo Producto."""
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def get_stock_total(self):
        """
        Calcula y retorna el stock total físico disponible para el producto.
        
        Realiza una consulta de agregación sobre los lotes asociados para sumar
        sus cantidades actuales ('cantidad_actual'). Provee la fuente de verdad
        para el inventario en tiempo real.
        
        Returns:
            Decimal: La suma total de las cantidades de los lotes. Retorna 0 si no hay lotes.
        """
        # Agregación mediante ORM de Django.
        total = self.lotes.aggregate(total_stock=Sum('cantidad_actual'))['total_stock']
        return total if total is not None else 0
    
    def __str__(self):
        """Retorna el nombre del producto como su representación."""
        return self.nombre

class Lote(models.Model):
    """
    Representa una partida específica de ingreso de mercadería al inventario.
    
    Implementa el modelo de gestión de inventario por lotes, lo cual es esencial para:
    1. Trazabilidad de ingresos.
    2. Gestión de múltiples fechas de vencimiento para un mismo SKU (Stock Keeping Unit).
    3. Cálculo de costos promedios o específicos (FIFO/LIFO).
    """
    # Relación con el producto padre.
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE, # Si se elimina el producto, se eliminan sus lotes.
        related_name='lotes'
    )
    # Stock remanente en este lote específico.
    cantidad_actual = models.DecimalField('Cantidad Actual', max_digits=10, decimal_places=3)
    
    # Datos económicos y de caducidad del lote.
    precio_compra = models.DecimalField('Precio de Compra del Lote', max_digits=10, decimal_places=2, default=0)
    fecha_vencimiento = models.DateField('Fecha de Vencimiento', null=True, blank=True)
    
    # Auditoría de ingreso.
    fecha_ingreso = models.DateField(auto_now_add=True)
    
    class Meta:
        """Metadatos para la configuración del modelo Lote."""
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        # Ordenamiento por vencimiento para facilitar estrategias FEFO (First Expired, First Out).
        ordering = ['fecha_vencimiento']

    def __str__(self):
        """Retorna una descripción del lote incluyendo producto y vencimiento."""
        return f'Lote de {self.producto.nombre} - Vence: {self.fecha_vencimiento}'