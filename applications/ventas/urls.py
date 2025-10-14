# applications/ventas/urls.py
from django.urls import path
from . import views

# --- AÑADE ESTA LÍNEA ---
app_name = 'ventas_app'

urlpatterns = [
    # Es posible que esta línea aún no la tuvieras,
    # la añadimos para que el enlace del Navbar funcione.
    path('pos/', views.POSView.as_view(), name='pos'),

    path('clientes/buscar/', views.buscar_clientes, name='buscar_clientes'),
    path('clientes/crear/', views.crear_cliente_modal, name='crear_cliente_modal'),

]