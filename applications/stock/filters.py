# applications/stock/filters.py

"""
Módulo de Filtros para la aplicación 'stock'.

Este archivo define los conjuntos de filtros (FilterSets) utilizados para facilitar
la búsqueda y segmentación de registros en las vistas de listado. Utiliza la librería
`django-filters` para crear formularios de filtrado dinámicos y eficientes.
"""

from django import forms
import django_filters
from django_select2.forms import Select2Widget
from .models import Producto, Marca, Categoria

class ProductFilter(django_filters.FilterSet):
    """
    Clase de filtro para el modelo Producto.

    Permite a los usuarios filtrar el listado de productos por nombre, marca y categoría.
    Integra widgets avanzados (Select2) para mejorar la experiencia de usuario en
    la selección de claves foráneas (marcas y categorías).
    """
    
    # Filtro de texto para el nombre del producto.
    # Realiza una búsqueda insensible a mayúsculas/minúsculas (icontains).
    nombre = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Filtro de selección para la Marca.
    # Utiliza 'Select2Widget' para proporcionar un dropdown con capacidad de búsqueda,
    # lo cual es útil cuando existen muchas marcas registradas.
    marca = django_filters.ModelChoiceFilter(
        queryset=Marca.objects.all(),
        widget=Select2Widget(attrs={'class': 'form-control'}),
        label='Marca'
    )
    
    # Filtro de selección para la Categoría.
    # Similar al de marca, utiliza 'Select2Widget' para facilitar la selección.
    categoria = django_filters.ModelChoiceFilter(
        queryset=Categoria.objects.all(),
        widget=Select2Widget(attrs={'class': 'form-control'}),
        label='Categoría'
    )

    class Meta:
        """Metadatos de configuración del FilterSet."""
        model = Producto
        fields = ['nombre', 'marca', 'categoria']