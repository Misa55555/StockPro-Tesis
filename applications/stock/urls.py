# applications/stock/urls.py

"""
Configuración de URLs para la aplicación 'stock'.

Este módulo define el esquema de enrutamiento para la gestión del inventario.
Establece las rutas de acceso para las operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
sobre Productos, Categorías y Marcas, así como para funcionalidades específicas
como la carga de lotes, reportes y actualizaciones masivas de precios.
"""

from django.urls import path
from . import views

# Definición del namespace de la aplicación.
# Permite referenciar las URLs de manera única (ej. 'stock_app:product_list')
# en plantillas y redirecciones, evitando colisiones con otras aplicaciones.
app_name = 'stock_app'

urlpatterns = [
    # --- Gestión de Productos ---
    # Rutas para el ciclo de vida completo de los productos.
    path('stock/', views.ProductListView.as_view(), name='product_list'),
    path('stock/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('stock/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),
    # Ruta específica para la eliminación, apuntando a una función de modal para confirmación.
    path('stock/delete/<int:pk>/', views.product_delete_modal, name='product_delete'),
    
    # --- Gestión de Categorías ---
    # Rutas para la administración de las categorías de clasificación.
    path('categorias/', views.CategoryListView.as_view(), name='category_list'),
    path('categorias/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categorias/edit/<int:pk>/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categorias/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # --- Gestión de Marcas ---
    # Rutas para la administración de las marcas comerciales.
    path('marcas/', views.MarcaListView.as_view(), name='marca_list'),
    path('marcas/add/', views.MarcaCreateView.as_view(), name='marca_add'),
    path('marcas/edit/<int:pk>/', views.MarcaUpdateView.as_view(), name='marca_edit'),
    path('marcas/delete/<int:pk>/', views.MarcaDeleteView.as_view(), name='marca_delete'),
    # Ruta especializada para la actualización masiva de precios por marca.
    path('marcas/update-prices/<int:pk>/', views.marca_update_prices, name='marca_update_prices'),

    # --- Gestión de Lotes y Reportes ---
    # Rutas operativas para el ingreso de stock y generación de informes.
    path('stock/cargar-lote/', views.CargarLoteView.as_view(), name='cargar_lote'),
    path('stock/exportar-excel/', views.exportar_stock_excel, name='exportar_stock_excel'),
    # Endpoint de API para obtener detalles de producto asíncronamente (AJAX).
    path('api/producto/details/', views.get_producto_details, name='api_product_details'),
    # Ruta para la eliminación de un lote de stock específico.
    path('stock/lote/delete/<int:pk>/', views.lote_delete, name='lote_delete'),
    
    # --- Cambios de Estado (Toggle) ---
    # Rutas funcionales para alternar el estado (activo/inactivo) de entidades sin eliminarlas físicamente.
    path('stock/toggle/<int:pk>/', views.toggle_product_status, name='product_toggle'),
    path('categorias/toggle/<int:pk>/', views.toggle_category_status, name='category_toggle'),
    path('marcas/toggle/<int:pk>/', views.toggle_marca_status, name='marca_toggle'),
]