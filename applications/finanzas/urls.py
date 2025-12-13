# applications/finanzas/urls.py

"""
Configuración de URLs para la aplicación 'finanzas'.

Este módulo establece el esquema de enrutamiento para el módulo financiero del sistema.
Define las rutas de acceso para el dashboard de control, los endpoints de la API
que alimentan los gráficos, los procesos de registro de gastos y la generación
de reportes exportables.
"""

from django.urls import path
from . import views

# Definición del namespace de la aplicación.
# Facilita la referencia inversa de URLs en plantillas y código (ej. 'finanzas_app:dashboard').
app_name = 'finanzas_app'

urlpatterns = [
    # 1. La página HTML del dashboard
    # Mapea la URL base del dashboard a la vista que renderiza la plantilla principal.
    path(
        'dashboard/', 
        views.DashboardFinanzasView.as_view(), 
        name='dashboard'
    ),
    
    # 2. El Endpoint de datos JSON para Chart.js
    # Ruta API que retorna los indicadores y datos financieros en formato JSON
    # para ser consumidos asíncronamente por las librerías de gráficos en el frontend.
    path(
        'api/data/', 
        views.FinanzasDataJSONView.as_view(), 
        name='api_data'
    ),
    
    # 3. El Endpoint para guardar el formulario de gasto
    # Ruta encargada de procesar la solicitud POST para la persistencia de nuevos gastos.
    path(
        'registrar-gasto/', 
        views.RegistrarGastoView.as_view(), 
        name='registrar_gasto'
    ),
    
    # 4. El Endpoint para guardar la nueva categoría de gasto
    # Ruta para la creación dinámica de categorías de gastos desde la interfaz de usuario.
    path(
        'registrar-categoria-gasto/', 
        views.RegistrarCategoriaGastoView.as_view(), 
        name='registrar_categoria_gasto'
    ),
    
    # 5. El Endpoint para descargar el reporte de Excel
    # Ruta que genera y sirve el archivo de hoja de cálculo con el reporte financiero detallado.
    path(
        'exportar-excel/', 
        views.ExportarExcelView.as_view(), 
        name='exportar_excel'
    ),
]