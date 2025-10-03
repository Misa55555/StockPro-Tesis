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
    Representa la marca de un producto (ej. Coca-Cola, Bimbo, Lays).
    
    Este modelo permite agrupar productos bajo un mismo fabricante, facilitando
    la búsqueda, la generación de reportes y la gestión de inventario.
    """
    # Campo para el nombre único de la marca.
    nombre = models.CharField(
        'Nombre de la Marca',
        max_length=100,
        unique=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        """Metadatos para el modelo Marca."""
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre'] # Ordena las marcas alfabéticamente.

    def __str__(self):
        """Representación en cadena de texto del objeto Marca."""
        return self.nombre

class UnidadMedida(models.Model):
    """
    Define las unidades en que se miden los productos (ej. Unidad, Kilogramo, Litro).
    
    Es un modelo crucial para la correcta gestión del stock fraccionable y para
    estandarizar la forma en que se cuantifican los productos.
    """
    # Nombre completo de la unidad de medida.
    nombre = models.CharField(
        'Unidad de Medida',
        max_length=50,
        unique=True
    )
    # Abreviatura estándar (ej. "un", "kg", "L").
    abreviatura = models.CharField(
        'Abreviatura',
        max_length=10
    )

    class Meta:
        """Metadatos para el modelo UnidadMedida."""
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['nombre']

    def __str__(self):
        """Representación en cadena de texto del objeto UnidadMedida."""
        return self.nombre

class Categoria(models.Model):
    """
    Clasificación de los productos en categorías (ej. Bebidas, Lácteos, Panificados).
    
    Este modelo es fundamental para la organización del inventario y la navegación
    del cliente en el portal online, permitiendo filtrar y encontrar productos
    de manera eficiente.
    """
    # Nombre único de la categoría.
    nombre = models.CharField(
        'Nombre',
        max_length=100,
        unique=True
    )
    # Campo booleano para controlar la visibilidad de la categoría en el portal de clientes.
    es_visible_online = models.BooleanField(
        'Visible en portal cliente',
        default=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        """Metadatos para el modelo Categoria."""
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        """Representación en cadena de texto del objeto Categoria."""
        return self.nombre

class Producto(models.Model):
    """
    Entidad central del módulo de stock que representa un artículo vendible.
    
    Este modelo agrupa toda la información comercial y de gestión de un producto.
    No almacena el stock directamente; en su lugar, el stock total se calcula
    dinámicamente a partir de la suma de sus Lotes asociados.
    """
    # Atributos comerciales y descriptivos del producto.
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    precio_venta = models.DecimalField('Precio de Venta', max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField('Stock Mínimo de Alerta', max_digits=10, decimal_places=3, default=5.000)
    es_visible_online = models.BooleanField('Visible en portal cliente', default=True)
    is_active = models.BooleanField(default=True)
    codigo_barras = models.CharField('Código de Barras', max_length=100, blank=True, null=True, unique=True)

    # Relaciones con otros modelos para clasificar el producto.
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL, # Si se borra la categoría, este campo se pone nulo.
        null=True, blank=True, related_name='productos'
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL, # Si se borra la marca, este campo se pone nulo.
        null=True, blank=True, related_name='productos'
    )
    unidad_medida = models.ForeignKey(
        UnidadMedida,
        on_delete=models.PROTECT # Impide eliminar una Unidad de Medida si está en uso por un producto.
    )

    class Meta:
        """Metadatos para el modelo Producto."""
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def get_stock_total(self):
        """
        Calcula y retorna el stock total disponible para el producto.
        
        Este método realiza una consulta de agregación sobre los lotes asociados
        para sumar sus cantidades actuales, proveyendo una única fuente de verdad
        para el stock del producto en tiempo real.
        """
        # Utiliza el ORM de Django para sumar el campo 'cantidad_actual' de todos los lotes relacionados.
        total = self.lotes.aggregate(total_stock=Sum('cantidad_actual'))['total_stock']
        # Retorna 0 si no hay lotes asociados para evitar un valor Nulo (None).
        return total if total is not None else 0
    
    def __str__(self):
        """Representación en cadena de texto del objeto Producto."""
        return self.nombre

class Lote(models.Model):
    """
    Representa una partida específica de un producto que ingresó al inventario.
    
    Este modelo es la clave para la gestión de stock. Cada vez que se compra
    mercadería de un producto, se crea un nuevo lote. Esto permite manejar
    múltiples fechas de vencimiento para un mismo producto y llevar un
    control preciso de las existencias.
    """
    # Relación con el producto al que pertenece el lote.
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE, # Si se elimina el producto, se eliminan todos sus lotes.
        related_name='lotes'
    )
    # Cantidad de unidades de este lote que quedan en stock.
    cantidad_actual = models.DecimalField('Cantidad Actual', max_digits=10, decimal_places=3)
    # Precio de compra del producto (opcional).
    precio_compra = models.DecimalField('Precio de Compra del Lote', max_digits=10, decimal_places=2, default=0)
    # Fecha de vencimiento del lote (opcional).
    fecha_vencimiento = models.DateField('Fecha de Vencimiento', null=True, blank=True)
    # Fecha en que el lote fue registrado en el sistema (se establece automáticamente).
    fecha_ingreso = models.DateField(auto_now_add=True)
    
    class Meta:
        """Metadatos para el modelo Lote."""
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        # Ordena los lotes por fecha de vencimiento, para facilitar la gestión FIFO/FEFO.
        ordering = ['fecha_vencimiento']

    def __str__(self):
        """Representación en cadena de texto del objeto Lote."""
        return f'Lote de {self.producto.nombre} - Vence: {self.fecha_vencimiento}'