# applications/stock/filters.py
import django_filters
from .models import Producto

class ProductFilter(django_filters.FilterSet):
    # Añadimos un filtro para buscar por nombre, ignorando mayúsculas/minúsculas
    nombre = django_filters.CharFilter(lookup_expr='icontains', label='Nombre del Producto')

    class Meta:
        model = Producto
        # Campos por los que podremos filtrar
        fields = ['nombre', 'marca', 'categoria']