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


# --- Vistas de Producto ---
class ProductListView(ListView):
    model = Producto
    template_name = "stock/product_list.html"
    context_object_name = 'productos'
    
    # --- INICIO DE LA LÓGICA DE FILTROS ---
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context
    # --- FIN DE LA LÓGICA DE FILTROS ---

class ProductCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "stock/product_form.html"
    success_url = reverse_lazy('stock_app:product_list')

class ProductUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "stock/product_form.html"
    success_url = reverse_lazy('stock_app:product_list')

class ProductDeleteView(DeleteView):
    model = Producto
    template_name = "stock/product_confirm_delete.html"
    success_url = reverse_lazy('stock_app:product_list')


# --- Vistas de Categoría ---
class CategoryListView(ListView):
    model = Categoria
    template_name = "stock/category_list.html"
    context_object_name = 'categorias'

class CategoryCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "stock/partials/category_form.html"
    success_url = reverse_lazy('stock_app:category_list')

    def form_valid(self, form):
        form.save()
        return HttpResponse(status=204)

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

class MarcaCreateView(CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = "stock/partials/marca_form.html"
    success_url = reverse_lazy('stock_app:marca_list')

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
        lote = form.save(commit=False)
        lote.cantidad_inicial = lote.cantidad_actual
        lote.save()
        return super().form_valid(form)

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