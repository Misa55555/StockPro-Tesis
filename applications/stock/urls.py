# applications/stock/urls.py
from django.urls import path
from . import views

app_name = 'stock_app'

urlpatterns = [
    # URLs de Producto
    path('stock/', views.ProductListView.as_view(), name='product_list'),
    path('stock/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('stock/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),
    # --- CAMBIO: Esta línea ahora apunta a la nueva función de modal ---
    path('stock/delete/<int:pk>/', views.product_delete_modal, name='product_delete'),
    
    # URLs de Categorías
    path('categorias/', views.CategoryListView.as_view(), name='category_list'),
    path('categorias/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categorias/edit/<int:pk>/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categorias/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # URLs de Marcas
    path('marcas/', views.MarcaListView.as_view(), name='marca_list'),
    path('marcas/add/', views.MarcaCreateView.as_view(), name='marca_add'),
    path('marcas/edit/<int:pk>/', views.MarcaUpdateView.as_view(), name='marca_edit'),
    path('marcas/delete/<int:pk>/', views.MarcaDeleteView.as_view(), name='marca_delete'),
    path('marcas/update-prices/<int:pk>/', views.marca_update_prices, name='marca_update_prices'),

    # URLs de Lotes y Reportes
    path('stock/cargar-lote/', views.CargarLoteView.as_view(), name='cargar_lote'),
    path('stock/exportar-excel/', views.exportar_stock_excel, name='exportar_stock_excel'),
    path('api/producto/details/', views.get_producto_details, name='api_product_details'),
    path('stock/lote/delete/<int:pk>/', views.lote_delete, name='lote_delete'),
    
    # URLs de Toggle (Ocultar/Restaurar)
    path('stock/toggle/<int:pk>/', views.toggle_product_status, name='product_toggle'),
    path('categorias/toggle/<int:pk>/', views.toggle_category_status, name='category_toggle'),
    path('marcas/toggle/<int:pk>/', views.toggle_marca_status, name='marca_toggle'),
]