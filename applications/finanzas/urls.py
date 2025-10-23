# applications/finanzas/urls.py
from django.urls import path
from . import views

app_name = 'finanzas_app'

urlpatterns = [
    # 1. La página HTML del dashboard
    path(
        'dashboard/', 
        views.DashboardFinanzasView.as_view(), 
        name='dashboard'
    ),
    
    # 2. El Endpoint de datos JSON para Chart.js
    path(
        'api/data/', 
        views.FinanzasDataJSONView.as_view(), 
        name='api_data'
    ),
    
    # 3. El Endpoint para guardar el formulario de gasto
    path(
        'registrar-gasto/', 
        views.RegistrarGastoView.as_view(), 
        name='registrar_gasto'
    ),
    
    # 4. El Endpoint para guardar la nueva categoría de gasto
    path(
        'registrar-categoria-gasto/', 
        views.RegistrarCategoriaGastoView.as_view(), 
        name='registrar_categoria_gasto'
    ),
    
    # 5. ¡NUEVO! El Endpoint para descargar el reporte de Excel
    path(
        'exportar-excel/', 
        views.ExportarExcelView.as_view(), 
        name='exportar_excel'
    ),
]