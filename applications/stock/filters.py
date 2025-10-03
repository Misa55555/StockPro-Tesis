# applications/stock/filters.py
from django import forms
import django_filters
from django_select2.forms import Select2Widget
from .models import Producto, Marca, Categoria

class ProductFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Le decimos explícitamente que use un ModelChoiceFilter con el widget de Select2
    marca = django_filters.ModelChoiceFilter(
        queryset=Marca.objects.all(),
        widget=Select2Widget(attrs={'class': 'form-control'}),
        label='Marca'
    )
    categoria = django_filters.ModelChoiceFilter(
        queryset=Categoria.objects.all(),
        widget=Select2Widget(attrs={'class': 'form-control'}),
        label='Categoría'
    )
    # --- FIN DE LA CORRECCIÓN ---

    class Meta:
        model = Producto
        fields = ['nombre', 'marca', 'categoria']