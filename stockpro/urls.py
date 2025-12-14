# stockpro/urls.py

"""
Configuración de URLs principal del proyecto StockPro.

Este módulo define el esquema de enrutamiento global del sistema. Actúa como
el despachador central (URL Dispatcher), delegando las solicitudes HTTP a las
configuraciones de URL específicas de cada aplicación modular (Dashboard, Stock,
Ventas, etc.) basándose en los prefijos de ruta.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Interfaz de administración nativa de Django.
    # Proporciona acceso CRUD directo a la base de datos para superusuarios.
    path('admin/', admin.site.urls),

    # Aplicación Dashboard.
    # Se configura en la raíz ('') para ser la página de aterrizaje tras el login.
    # Gestiona la vista principal y los indicadores clave.
    path('', include('applications.dashboard.urls')),

    # Sistema de Autenticación.
    # Incluye las rutas estándar de Django para inicio de sesión, cierre de sesión
    # y gestión de contraseñas.
    path('accounts/', include('django.contrib.auth.urls')),

    # Aplicación de Stock.
    # Gestiona el inventario, catálogo de productos, lotes, marcas y categorías.
    path('app/', include('applications.stock.urls')),

    # Aplicación de Cierres.
    # Gestiona los procesos de arqueo y cierre de caja.
    path('cierres/', include('applications.cierres.urls')),

    # Aplicación de Ventas.
    # Contiene la lógica del Punto de Venta (POS), facturación y gestión de clientes.
    path('ventas/', include('applications.ventas.urls')),

    # Rutas para Django Select2.
    # Habilita los endpoints necesarios para que los widgets de selección con autocompletado
    # (AJAX) funcionen correctamente en los formularios.
    path('select2/', include('django_select2.urls')),

    # Aplicación de Finanzas.
    # Gestiona el registro de gastos operativos, categorías de gastos y reportes financieros.
    path('finanzas/', include('applications.finanzas.urls')),
]