# applications/stock/views.py

"""
Módulo de Vistas para la aplicación 'stock'.

Este archivo contiene la lógica de negocio y la gestión de la interfaz de usuario
para el módulo de inventario. Define las Vistas Basadas en Clases (CBV) y las funciones
necesarias para realizar operaciones CRUD sobre Productos, Categorías, Marcas y Lotes.

Funcionalidades clave incluidas:
- Listados con filtrado avanzado y paginación.
- Creación y edición de entidades mediante formularios modales y estándar.
- Gestión de stock mediante el sistema de Lotes (Ingresos).
- Actualizaciones masivas de precios.
- Exportación de reportes a Excel.
- Control de estado (Activo/Inactivo) para "borrado lógico".
"""

from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.contrib import messages
import openpyxl
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction, IntegrityError 
from django.utils import timezone
from .forms import ActualizarPrecioMarcaForm 
from .filters import ProductFilter
# Importamos TODOS los modelos
from .models import Producto, Categoria, Marca, UnidadMedida, Lote
# Importamos TODOS los formularios
from .forms import ProductoForm, CategoriaForm, MarcaForm, LoteForm
from django.db import IntegrityError

# ==========================================
# VISTAS DE PRODUCTOS
# ==========================================

class ProductListView(ListView):
    """
    Vista de listado para el catálogo de Productos.

    Gestiona la visualización del inventario principal, integrando filtros de búsqueda
    (por nombre, marca, categoría) y la opción de mostrar/ocultar productos inactivos.
    Utiliza 'select_related' y 'prefetch_related' para optimizar las consultas a la base de datos.
    """
    model = Producto
    template_name = "stock/product_list.html"
    context_object_name = 'productos'

    def get_queryset(self):
        """
        Construye el conjunto de datos (queryset) filtrado.
        
        1. Pre-carga relaciones para evitar el problema de N+1 consultas.
        2. Aplica el filtro de estado (activo/inactivo) según los parámetros GET.
        3. Aplica los filtros avanzados definidos en ProductFilter.
        """
        # Optimización de consultas: trae datos relacionados en la misma query.
        queryset = super().get_queryset().select_related(
            'marca', 'categoria', 'unidad_medida'
        ).prefetch_related('lotes')
        
        # Lógica para mostrar u ocultar productos desactivados (soft-deleted).
        mostrar_ocultos = self.request.GET.get('mostrar_ocultos')
        if mostrar_ocultos:
            queryset = queryset.filter(is_active=False)
        else:
            queryset = queryset.filter(is_active=True)
            
        # Aplicación del FilterSet (django-filters).
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        """
        Agrega datos adicionales al contexto de la plantilla.
        
        Incluye el formulario de filtrado y el estado del checkbox 'mostrar_ocultos'
        para mantener la persistencia de la interfaz.
        """
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        context["mostrar_ocultos"] = self.request.GET.get('mostrar_ocultos')
        # Sobrescribimos 'productos' con el queryset filtrado explícitamente.
        context['productos'] = self.get_queryset()
        context['today'] = timezone.now().date() # Para validaciones visuales de fecha (vencimientos).
        return context

class ProductCreateView(CreateView):
    """
    Vista para el alta de nuevos Productos.
    Renderiza el formulario completo de producto y redirige al listado tras el éxito.
    """
    model = Producto
    form_class = ProductoForm
    template_name = "stock/product_form.html"
    success_url = reverse_lazy('stock_app:product_list')

class ProductUpdateView(UpdateView):
    """
    Vista para la edición de Productos existentes.
    Utiliza un template parcial para ser renderizado dentro de un modal.
    """
    model = Producto
    form_class = ProductoForm
    template_name = "stock/partials/product_form_modal.html"
    success_url = reverse_lazy('stock_app:product_list')

    def get_form(self, form_class=None):
        """
        Personaliza el formulario antes de mostrarlo.
        Filtra los selectores de Categoría y Marca para mostrar solo opciones activas.
        """
        form = super().get_form(form_class)
        form.fields['categoria'].queryset = Categoria.objects.filter(is_active=True)
        form.fields['marca'].queryset = Marca.objects.filter(is_active=True)
        return form

def product_delete_modal(request, pk):
    """
    Vista funcional para la eliminación física de un producto.
    
    Se utiliza con precaución, ya que la eliminación física borra el historial.
    Generalmente se prefiere la desactivación (toggle_product_status).
    """
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    messages.success(request, f'El producto "{producto.nombre}" ha sido eliminado permanentemente.')
    return redirect('stock_app:product_list')


# ==========================================
# VISTAS DE CATEGORÍA
# ==========================================

class CategoryListView(ListView):
    """
    Vista de listado para la gestión de Categorías.
    Permite visualizar categorías activas e inactivas.
    """
    model = Categoria
    template_name = "stock/category_list.html"
    context_object_name = 'categorias'

    def get_queryset(self):
        # Filtra según el parámetro GET 'mostrar_ocultos'.
        if self.request.GET.get('mostrar_ocultos'):
            return Categoria.objects.filter(is_active=False)
        return Categoria.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mostrar_ocultos"] = self.request.GET.get('mostrar_ocultos')
        return context

class CategoryCreateView(CreateView):
    """
    Vista para crear Categorías. Soporta peticiones AJAX para modales dinámicos.
    """
    model = Categoria
    form_class = CategoriaForm
    template_name = "stock/partials/category_form.html"
    success_url = reverse_lazy('stock_app:category_list')

    def form_valid(self, form):
        """
        Maneja el guardado del formulario exitoso.
        
        Implementa lógica dual:
        1. AJAX: Retorna JSON con los datos de la nueva categoría (útil para selects dinámicos).
        2. Estándar: Redirige o renderiza según el flujo normal.
        """
        # 1. Intento AJAX (Solicitudes desde modales/popups)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                self.object = form.save()
                return JsonResponse({
                    'status': 'success',
                    'id': self.object.pk,
                    'nombre': self.object.nombre,
                    'type': 'categoria'
                })
            except IntegrityError:
                # Manejo de error de unicidad (nombre duplicado)
                return JsonResponse({
                    'status': 'error',
                    'message': f'La categoría "{form.instance.nombre}" ya existe.'
                }, status=400)
        
        # 2. Intento Normal (Fallback para navegación estándar)
        try:
            self.object = form.save()
            return super().form_valid(form)
        except IntegrityError:
             form.add_error('nombre', f'La categoría "{form.instance.nombre}" ya existe.')
             return self.form_invalid(form)

    def form_invalid(self, form):
        """Retorna errores en formato JSON si la petición es AJAX."""
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors.as_json(),
                'message': 'Verifique los datos ingresados.'
            }, status=400)
        return super().form_invalid(form)


class CategoryUpdateView(UpdateView):
    """Vista para editar categorías existentes."""
    model = Categoria
    form_class = CategoriaForm
    template_name = "stock/partials/category_form.html"
    success_url = reverse_lazy('stock_app:category_list')

class CategoryDeleteView(DeleteView):
    """Vista de confirmación para eliminar categorías."""
    model = Categoria
    template_name = "stock/partials/category_confirm_delete.html"
    success_url = reverse_lazy('stock_app:category_list')

# ==========================================
# VISTAS DE MARCA
# ==========================================

class MarcaListView(ListView):
    """
    Vista de listado para la gestión de Marcas.
    """
    model = Marca
    template_name = "stock/marca_list.html"
    context_object_name = 'marcas'

    def get_queryset(self):
        if self.request.GET.get('mostrar_ocultos'):
            return Marca.objects.filter(is_active=False)
        return Marca.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mostrar_ocultos"] = self.request.GET.get('mostrar_ocultos')
        return context

class MarcaCreateView(CreateView):
    """
    Vista para crear Marcas. Soporta peticiones AJAX para creación rápida desde producto.
    """
    model = Marca
    form_class = MarcaForm
    template_name = "stock/partials/marca_form.html"
    success_url = reverse_lazy('stock_app:marca_list')

    def form_valid(self, form):
        # Lógica AJAX similar a CategoryCreateView
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                self.object = form.save()
                return JsonResponse({
                    'status': 'success',
                    'id': self.object.pk,
                    'nombre': self.object.nombre,
                    'type': 'marca'
                })
            except IntegrityError:
                # Captura el error de duplicado de base de datos
                return JsonResponse({
                    'status': 'error',
                    'message': f'La marca "{form.instance.nombre}" ya existe.'
                }, status=400)

        # Comportamiento normal no-AJAX (Renderiza opciones actualizadas)
        self.object = form.save()
        context = {'marcas': Marca.objects.all()}
        return render(self.request, 'stock/partials/marca_options.html', context)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors.as_json(),
                'message': 'Error de validación en el formulario.'
            }, status=400)
        return super().form_invalid(form)

class MarcaUpdateView(UpdateView):
    """Vista para editar marcas existentes."""
    model = Marca
    form_class = MarcaForm
    template_name = "stock/partials/marca_form.html"
    success_url = reverse_lazy('stock_app:marca_list')

class MarcaDeleteView(DeleteView):
    """Vista de confirmación para eliminar marcas."""
    model = Marca
    template_name = "stock/partials/marca_confirm_delete.html"
    success_url = reverse_lazy('stock_app:marca_list')

# ==========================================
# GESTIÓN DE LOTES Y OPERACIONES
# ==========================================

class CargarLoteView(CreateView):
    """
    Vista compleja para la carga de nuevos Lotes de stock (Ingresos).

    Además de crear el lote, permite actualizar opcionalmente el precio de venta
    del producto asociado en una sola operación transaccional.
    """
    model = Lote
    form_class = LoteForm
    template_name = "stock/cargar_lote.html"
    success_url = reverse_lazy('stock_app:product_list')

    def form_valid(self, form):
        """
        Ejecuta la lógica de negocio dentro de una transacción atómica.
        1. Guarda el Lote.
        2. Si se solicitó, actualiza el precio de venta del Producto padre.
        """
        with transaction.atomic():
            lote = form.save(commit=False)
            lote.save()

            # Lógica opcional de actualización de precios
            if form.cleaned_data.get('actualizar_precio') and form.cleaned_data.get('nuevo_precio_venta'):
                nuevo_precio = form.cleaned_data.get('nuevo_precio_venta')
                producto = lote.producto
                producto.precio_venta = nuevo_precio
                producto.save()
                messages.success(self.request, f"Se cargó el stock y se actualizó el precio de {producto.nombre} a ${nuevo_precio}")
            else:
                messages.success(self.request, "Stock cargado correctamente.")

        return super(CreateView, self).form_valid(form)

def lote_delete(request, pk):
    """
    Elimina un lote específico. 
    Útil para corregir errores de carga de inventario.
    """
    lote = get_object_or_404(Lote, pk=pk)
    producto_nombre = lote.producto.nombre
    lote.delete()
    messages.success(request, f'Se ha eliminado un lote de {producto_nombre}.')
    return redirect('stock_app:product_list')

def exportar_stock_excel(request):
    """
    Genera y descarga un reporte de stock en formato Excel (.xlsx).
    
    Incluye columnas calculadas como el 'Stock Total' derivado de los lotes.
    """
    productos = Producto.objects.all()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Reporte de Stock'
    headers = ['Nombre', 'Marca', 'Categoría', 'Unidad', 'Stock Total', 'Stock Mínimo', 'Precio de Venta']
    sheet.append(headers)
    for producto in productos:
        # Calcula el stock total dinámicamente
        stock_total = producto.get_stock_total()
        sheet.append([
            producto.nombre,
            producto.marca.nombre if producto.marca else 'N/A',
            producto.categoria.nombre if producto.categoria else 'N/A',
            producto.unidad_medida.abreviatura,
            stock_total,
            producto.stock_minimo,
            producto.precio_venta,
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_stock.xlsx"'
    workbook.save(response)
    return response

# ==========================================
# CAMBIOS DE ESTADO (SOFT DELETE / TOGGLE)
# ==========================================

def toggle_product_status(request, pk):
    """Alterna el estado activo/inactivo de un producto."""
    producto = get_object_or_404(Producto, pk=pk)
    producto.is_active = not producto.is_active
    producto.save()
    messages.info(request, f'El estado del producto "{producto.nombre}" ha sido actualizado.')
    return redirect('stock_app:product_list')

def toggle_category_status(request, pk):
    """Alterna el estado activo/inactivo de una categoría."""
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.is_active = not categoria.is_active
    categoria.save()
    messages.info(request, f'El estado de la categoría "{categoria.nombre}" ha sido actualizado.')
    return redirect('stock_app:category_list')

def toggle_marca_status(request, pk):
    """Alterna el estado activo/inactivo de una marca."""
    marca = get_object_or_404(Marca, pk=pk)
    marca.is_active = not marca.is_active
    marca.save()
    messages.info(request, f'El estado de la marca "{marca.nombre}" ha sido actualizado.')
    return redirect('stock_app:marca_list')

# ==========================================
# UTILIDADES Y API
# ==========================================

def get_producto_details(request):
    """
    Endpoint de API (AJAX) para obtener detalles rápidos de un producto.
    Utilizado en el formulario de Lotes para precargar el precio actual.
    """
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            producto = Producto.objects.get(pk=product_id)
            return JsonResponse({
                'status': 'success',
                'precio_venta': producto.precio_venta
            })
        except Producto.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Falta ID'}, status=400)


def marca_update_prices(request, pk):
    """
    Vista funcional para la actualización masiva de precios por Marca.

    Permite aplicar un aumento o descuento porcentual a todos los productos
    pertenecientes a una marca seleccionada. Utiliza transacciones para asegurar
    que todos los precios se actualicen o ninguno en caso de fallo.
    """
    marca = get_object_or_404(Marca, pk=pk)
    
    if request.method == 'POST':
        form = ActualizarPrecioMarcaForm(request.POST)
        if form.is_valid():
            porcentaje = form.cleaned_data['porcentaje']
            
            # Convertimos el porcentaje a un factor multiplicador
            # Ej: 10% -> 1.10 | -10% -> 0.90
            factor = 1 + (porcentaje / 100)
            
            productos = Producto.objects.filter(marca=marca, is_active=True)
            count = 0
            
            try:
                # Bloque transaccional para actualización masiva segura
                with transaction.atomic():
                    for producto in productos:
                        # Calculamos nuevo precio
                        nuevo_precio = producto.precio_venta * factor
                        # Redondeamos a 2 decimales para consistencia monetaria
                        producto.precio_venta = round(nuevo_precio, 2)
                        producto.save()
                        count += 1
                
                messages.success(request, f'Se actualizaron los precios de {count} productos de "{marca.nombre}" correctamente.')
                # Cerramos el modal redirigiendo a la lista (el script JS recargará)
                return redirect('stock_app:marca_list')
                
            except Exception as e:
                messages.error(request, f'Error al actualizar precios: {str(e)}')
    else:
        form = ActualizarPrecioMarcaForm()

    context = {
        'form': form, 
        'marca': marca,
        'cantidad_productos': Producto.objects.filter(marca=marca, is_active=True).count()
    }
    return render(request, 'stock/partials/marca_update_prices.html', context)