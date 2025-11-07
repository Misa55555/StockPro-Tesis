# applications/stock/views.py
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.contrib import messages
import openpyxl
from .filters import ProductFilter
# Importamos TODOS los modelos que usamos en este archivo
from .models import Producto, Categoria, Marca, UnidadMedida, Lote
# Importamos TODOS los formularios que usamos
from .forms import ProductoForm, CategoriaForm, MarcaForm, LoteForm, UploadFileForm
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect # Añade get_object_or_404 y redirect
from django.http import JsonResponse
from django.db import transaction

# --- Vistas de Producto ---
class ProductListView(ListView):
    model = Producto
    template_name = "stock/product_list.html"
    context_object_name = 'productos' # Mantenemos esto por compatibilidad

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Lógica para mostrar/ocultar productos inactivos
        mostrar_ocultos = self.request.GET.get('mostrar_ocultos')
        if mostrar_ocultos:
            queryset = queryset.filter(is_active=False)
        else:
            queryset = queryset.filter(is_active=True)
            
        # Creamos el filterset con el queryset ya pre-filtrado por estado
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos el filterset completo a la plantilla
        context["filterset"] = self.filterset
        context["mostrar_ocultos"] = self.request.GET.get('mostrar_ocultos')
        # Pasamos la lista filtrada de productos a la variable 'productos'
        context['productos'] = self.get_queryset()
        return context

class ProductCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "stock/product_form.html"
    success_url = reverse_lazy('stock_app:product_list')

class ProductUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    # --- CAMBIO: Apuntamos a la nueva plantilla parcial ---
    template_name = "stock/partials/product_form_modal.html"
    success_url = reverse_lazy('stock_app:product_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Personalizamos los querysets después de crear el formulario
        form.fields['categoria'].queryset = Categoria.objects.filter(is_active=True)
        form.fields['marca'].queryset = Marca.objects.filter(is_active=True)
        # unidad_medida no necesita filtro especial
        return form

def product_delete_modal(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    messages.success(request, f'El producto "{producto.nombre}" ha sido eliminado permanentemente.')
    return redirect('stock_app:product_list')

# --- FIN DE LA CORRECCIÓN ---

# --- Vistas de Categoría ---
class CategoryListView(ListView):
    model = Categoria
    template_name = "stock/category_list.html"
    context_object_name = 'categorias'

    def get_queryset(self):
        if self.request.GET.get('mostrar_ocultos'):
            return Categoria.objects.filter(is_active=False)
        return Categoria.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mostrar_ocultos"] = self.request.GET.get('mostrar_ocultos')
        return context

class CategoryCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "stock/partials/category_form.html"
    # Simplemente redirigimos a la lista al tener éxito
    success_url = reverse_lazy('stock_app:category_list')


class CategoryUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "stock/partials/category_form.html"
    success_url = reverse_lazy('stock_app:category_list')

class CategoryDeleteView(DeleteView):
    model = Categoria
    template_name = "stock/partials/category_confirm_delete.html"
    success_url = reverse_lazy('stock_app:category_list')

# --- Vistas de Marca ---
class MarcaListView(ListView):
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
    model = Marca
    form_class = MarcaForm
    template_name = "stock/partials/marca_form.html"
    success_url = reverse_lazy('stock_app:marca_list')

    def form_valid(self, form):
        form.save()
        # Preparamos el contexto con todas las marcas
        context = {'marcas': Marca.objects.all()}
        # Renderizamos solo el parcial con las opciones
        return render(self.request, 'stock/partials/marca_options.html', context)

class MarcaUpdateView(UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = "stock/partials/marca_form.html"
    success_url = reverse_lazy('stock_app:marca_list')

class MarcaDeleteView(DeleteView):
    model = Marca
    template_name = "stock/partials/marca_confirm_delete.html"
    success_url = reverse_lazy('stock_app:marca_list')

# --- Vista para Cargar Lotes ---
class CargarLoteView(CreateView):
    model = Lote
    form_class = LoteForm
    template_name = "stock/cargar_lote.html"
    success_url = reverse_lazy('stock_app:product_list')

    def form_valid(self, form):
        # Usamos transaction.atomic para que si falla algo, no se guarde nada a medias
        with transaction.atomic():
            # 1. Guardamos el Lote normalmente
            lote = form.save(commit=False)
            # Aseguramos que cantidad inicial sea igual a la actual al crearlo
            # (asumiendo que tu modelo Lote tiene este campo si lo usas para históricos)
            # Si no tienes 'cantidad_inicial' en tu modelo Lote, borra esta línea:
            # lote.cantidad_inicial = lote.cantidad_actual 
            lote.save()

            # 2. Verificamos si hay que actualizar el precio del producto padre
            if form.cleaned_data.get('actualizar_precio') and form.cleaned_data.get('nuevo_precio_venta'):
                nuevo_precio = form.cleaned_data.get('nuevo_precio_venta')
                producto = lote.producto
                
                # Opcional: registrar en un log si el precio cambió
                if producto.precio_venta != nuevo_precio:
                     # Aquí podrías guardar un historial de precios si quisieras escalar a futuro
                     pass

                producto.precio_venta = nuevo_precio
                producto.save()
                messages.success(self.request, f"Se cargó el stock y se actualizó el precio de {producto.nombre} a ${nuevo_precio}")
            else:
                messages.success(self.request, "Stock cargado correctamente.")

        return super(CreateView, self).form_valid(form) # Llamamos al form_valid padre correctamente
# --- Vista de Importación de Excel ---
class ImportarProductosView(FormView):
    template_name = 'stock/importar_productos.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('stock_app:product_list')

    def form_valid(self, form):
        # ... (lógica de importación sin cambios)
        archivo = form.cleaned_data['file']
        workbook = openpyxl.load_workbook(archivo)
        sheet = workbook.active
        try:
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not any(row): continue
                nombre_producto, nombre_marca, nombre_categoria, nombre_unidad, precio_venta, stock_inicial = row
                marca, _ = Marca.objects.get_or_create(nombre=nombre_marca)
                categoria, _ = Categoria.objects.get_or_create(nombre=nombre_categoria)
                unidad, _ = UnidadMedida.objects.get_or_create(nombre=nombre_unidad, defaults={'abreviatura': nombre_unidad[:3].lower()})
                producto, created = Producto.objects.update_or_create(
                    nombre=nombre_producto,
                    defaults={'marca': marca, 'categoria': categoria, 'unidad_medida': unidad, 'precio_venta': precio_venta})
                if stock_inicial and float(stock_inicial) > 0:
                    Lote.objects.create(producto=producto, cantidad_inicial=stock_inicial, cantidad_actual=stock_inicial)
            messages.success(self.request, "¡Inventario importado correctamente!")
        except (ValueError, TypeError) as e:
            messages.error(self.request, f"Error al procesar el archivo: {e}")
            return self.form_invalid(form)
        return super().form_valid(form)


# --- VISTA DE EXPORTACIÓN (LA QUE FALTABA) ---
def exportar_stock_excel(request):
    productos = Producto.objects.all()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Reporte de Stock'
    headers = ['Nombre', 'Marca', 'Categoría', 'Unidad', 'Stock Total', 'Stock Mínimo', 'Precio de Venta']
    sheet.append(headers)
    for producto in productos:
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


def toggle_product_status(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.is_active = not producto.is_active
    producto.save()
    messages.info(request, f'El estado del producto "{producto.nombre}" ha sido actualizado.')
    return redirect('stock_app:product_list')

def toggle_category_status(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.is_active = not categoria.is_active
    categoria.save()
    messages.info(request, f'El estado de la categoría "{categoria.nombre}" ha sido actualizado.')
    return redirect('stock_app:category_list')

def toggle_marca_status(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    marca.is_active = not marca.is_active
    marca.save()
    messages.info(request, f'El estado de la marca "{marca.nombre}" ha sido actualizado.')
    return redirect('stock_app:marca_list')


# --- VISTA SUJERIDA POR EL PROFE ---
def get_producto_details(request):
    """Vista AJAX para obtener detalles de un producto seleccionado"""
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