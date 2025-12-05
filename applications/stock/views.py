# applications/stock/views.py
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.contrib import messages
import openpyxl
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction, IntegrityError # <--- IMPORTANTE: Importar IntegrityError
from django.utils import timezone
from .forms import ActualizarPrecioMarcaForm # Asegúrate de importar el nuevo form
from .filters import ProductFilter
# Importamos TODOS los modelos
from .models import Producto, Categoria, Marca, UnidadMedida, Lote
# Importamos TODOS los formularios
from .forms import ProductoForm, CategoriaForm, MarcaForm, LoteForm
from django.db import IntegrityError

# ... (Las Vistas de Producto ProductListView, ProductCreateView, etc. quedan IGUAL) ...
# ... (Solo copio aquí las que cambian para no hacer el mensaje eterno) ...

class ProductListView(ListView):
    model = Producto
    template_name = "stock/product_list.html"
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'marca', 'categoria', 'unidad_medida'
        ).prefetch_related('lotes')
        
        mostrar_ocultos = self.request.GET.get('mostrar_ocultos')
        if mostrar_ocultos:
            queryset = queryset.filter(is_active=False)
        else:
            queryset = queryset.filter(is_active=True)
            
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        context["mostrar_ocultos"] = self.request.GET.get('mostrar_ocultos')
        context['productos'] = self.get_queryset()
        context['today'] = timezone.now().date()
        return context

class ProductCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "stock/product_form.html"
    success_url = reverse_lazy('stock_app:product_list')

class ProductUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "stock/partials/product_form_modal.html"
    success_url = reverse_lazy('stock_app:product_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['categoria'].queryset = Categoria.objects.filter(is_active=True)
        form.fields['marca'].queryset = Marca.objects.filter(is_active=True)
        return form

def product_delete_modal(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    messages.success(request, f'El producto "{producto.nombre}" ha sido eliminado permanentemente.')
    return redirect('stock_app:product_list')


# --- Vistas de Categoría (MODIFICADA) ---
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
    success_url = reverse_lazy('stock_app:category_list')

    def form_valid(self, form):
        # 1. Intento AJAX
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
                return JsonResponse({
                    'status': 'error',
                    'message': f'La categoría "{form.instance.nombre}" ya existe.'
                }, status=400)
        
        # 2. Intento Normal (Fallback)
        try:
            self.object = form.save()
            # Si no es AJAX (ej. desde la lista), renderizamos las opciones o redirigimos
            # (Dependiendo de cómo lo uses en otros lados, aquí asumimos redirección o render simple)
            return super().form_valid(form)
        except IntegrityError:
             form.add_error('nombre', f'La categoría "{form.instance.nombre}" ya existe.')
             return self.form_invalid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors.as_json(),
                'message': 'Verifique los datos ingresados.'
            }, status=400)
        return super().form_invalid(form)


class CategoryUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "stock/partials/category_form.html"
    success_url = reverse_lazy('stock_app:category_list')

class CategoryDeleteView(DeleteView):
    model = Categoria
    template_name = "stock/partials/category_confirm_delete.html"
    success_url = reverse_lazy('stock_app:category_list')

# --- Vistas de Marca (MODIFICADA) ---
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
                # Captura el error de duplicado
                return JsonResponse({
                    'status': 'error',
                    'message': f'La marca "{form.instance.nombre}" ya existe.'
                }, status=400)

        # Comportamiento normal no-AJAX
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
    model = Marca
    form_class = MarcaForm
    template_name = "stock/partials/marca_form.html"
    success_url = reverse_lazy('stock_app:marca_list')

class MarcaDeleteView(DeleteView):
    model = Marca
    template_name = "stock/partials/marca_confirm_delete.html"
    success_url = reverse_lazy('stock_app:marca_list')

# ... (El resto de las vistas CargarLote, Exportar, Toggle, etc. quedan IGUAL) ...

class CargarLoteView(CreateView):
    model = Lote
    form_class = LoteForm
    template_name = "stock/cargar_lote.html"
    success_url = reverse_lazy('stock_app:product_list')

    def form_valid(self, form):
        with transaction.atomic():
            lote = form.save(commit=False)
            lote.save()

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
    lote = get_object_or_404(Lote, pk=pk)
    producto_nombre = lote.producto.nombre
    lote.delete()
    messages.success(request, f'Se ha eliminado un lote de {producto_nombre}.')
    return redirect('stock_app:product_list')

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

def get_producto_details(request):
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
                with transaction.atomic():
                    for producto in productos:
                        # Calculamos nuevo precio
                        nuevo_precio = producto.precio_venta * factor
                        # Redondeamos a 2 decimales (como pediste)
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