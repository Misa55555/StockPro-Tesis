# applications/stock/urls.py
from django.urls import path
from . import views

app_name = 'stock_app'

urlpatterns = [
    path('stock/', views.ProductListView.as_view(), name='product_list'),
    path('stock/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('stock/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('stock/delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('categorias/', views.CategoryListView.as_view(), name='category_list'),
    path('categorias/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categorias/edit/<int:pk>/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categorias/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('marcas/', views.MarcaListView.as_view(), name='marca_list'),
    path('marcas/add/', views.MarcaCreateView.as_view(), name='marca_add'),
    path('marcas/edit/<int:pk>/', views.MarcaUpdateView.as_view(), name='marca_edit'),
    path('marcas/delete/<int:pk>/', views.MarcaDeleteView.as_view(), name='marca_delete'),
    path('stock/cargar-lote/', views.CargarLoteView.as_view(), name='cargar_lote'),
    path('stock/exportar-excel/', views.exportar_stock_excel, name='exportar_stock_excel'),
    path('stock/importar-excel/', views.ImportarProductosView.as_view(), name='importar_stock_excel'),


]