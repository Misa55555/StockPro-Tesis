# applications/ventas/urls.py

"""
Configuración de URL para la aplicación de Ventas.

Este módulo define las rutas URL específicas para la gestión de ventas,
incluyendo el Punto de Venta (POS) y los endpoints asíncronos para
la gestión de clientes en tiempo real durante el proceso de venta.
"""

from django.urls import path
from . import views

# Definición del nombre de espacio (namespace) para la aplicación.
# Esto permite referenciar las URLs de forma única (ej. 'ventas_app:pos')
# evitando conflictos con otras aplicaciones del proyecto.
app_name = 'ventas_app'

urlpatterns = [
    # Ruta principal para la interfaz del Punto de Venta (POS).
    # Renderiza la vista basada en clases que gestiona la interfaz de facturación.
    path('pos/', views.POSView.as_view(), name='pos'),

    # Endpoint para la búsqueda asíncrona de clientes.
    # Utilizado por componentes de autocompletado (AJAX/Select2) en el frontend.
    path('clientes/buscar/', views.buscar_clientes, name='buscar_clientes'),

    # Endpoint para la creación rápida de clientes mediante ventana modal.
    # Permite registrar un nuevo cliente sin abandonar el flujo de la venta actual.
    path('clientes/crear/', views.crear_cliente_modal, name='crear_cliente_modal'),
]