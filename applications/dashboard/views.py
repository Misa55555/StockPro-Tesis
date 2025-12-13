# applications/dashboard/views.py

"""
Módulo de Vistas para la aplicación 'dashboard'.

Este archivo define la lógica de presentación del panel de control principal del sistema.
Su función es agregar y procesar métricas clave de negocio (KPIs) provenientes de
diferentes módulos (Ventas, Stock) para ofrecer una visión unificada del estado
operativo del comercio en tiempo real.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, F, Count, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

# --- Importamos los modelos necesarios ---
from applications.stock.models import Producto, Lote
from applications.ventas.models import Venta  # <--- IMPORTANTE: Importar el modelo Venta

@login_required
def dashboard_view(request):
    """
    Vista funcional que renderiza el Dashboard Principal.

    Realiza un procesamiento de datos para calcular:
    1. Alertas de inventario (stock bajo, agotado).
    2. Alertas de caducidad de lotes (vencidos, por vencer).
    3. Métricas de ventas del día actual (total facturado, cantidad de transacciones).

    Implementa control de acceso basado en roles (RBAC), restringiendo la visualización
    a usuarios con roles de 'Administrador' o 'Vendedor'.

    Args:
        request: El objeto HttpRequest.

    Returns:
        HttpResponse: La plantilla renderizada con el contexto de métricas y alertas.
        HttpResponseForbidden: Si el usuario no tiene el rol adecuado.
    """
    if not request.user.rol:
        return HttpResponseForbidden("<h1>Acceso Denegado: No tienes un rol asignado.</h1>")

    rol_usuario = request.user.rol.nombre

    if rol_usuario in ['Administrador', 'Vendedor']:
        
        # --- 1. LÓGICA DE STOCK (Alertas) ---
        # Recuperación de productos activos para análisis de inventario.
        productos_activos = Producto.objects.filter(is_active=True)

        # Cálculo del stock total físico sumando las cantidades de los lotes asociados.
        # Se utiliza Coalesce para asegurar que los productos sin lotes retornen 0 en lugar de None.
        productos_con_stock = productos_activos.annotate(
            stock_total=Coalesce(Sum('lotes__cantidad_actual'), 0, output_field=DecimalField())
        )

        # Alerta 1: Productos con Stock Bajo
        # Identifica productos con existencia positiva pero igual o inferior al umbral mínimo definido.
        productos_bajos_stock = productos_con_stock.filter(
            stock_total__gt=0,
            stock_total__lte=F('stock_minimo')
        )

        # Alerta 2: Productos sin Stock
        # Identifica productos que no tienen existencia física registrada (stock total = 0).
        productos_sin_lotes = productos_con_stock.filter(stock_total=0)
        
        hoy = timezone.now().date()
        proxima_semana = hoy + timedelta(days=7)

        # Alertas de Vencimiento
        # Lotes que vencen en el rango de hoy a 7 días (Próximos a vencer).
        lotes_por_vencer = Lote.objects.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=proxima_semana,
            cantidad_actual__gt=0  # Solo considera lotes con stock remanente.
        ).select_related('producto')

        # Lotes cuya fecha de vencimiento es anterior a hoy (Vencidos).
        lotes_vencidos = Lote.objects.filter(
            fecha_vencimiento__lt=hoy,
            cantidad_actual__gt=0
        ).select_related('producto')

        # --- 2. LÓGICA DE VENTAS DEL DÍA (Corrección) ---
        # Filtramos todas las ventas cuya fecha coincida con hoy
        ventas_de_hoy = Venta.objects.filter(fecha_hora__date=hoy)

        # Calculamos la suma total de dinero (campo 'total')
        # Si no hay ventas, aggregate devuelve None, por eso usamos 'or 0'
        total_ventas_dia = ventas_de_hoy.aggregate(total=Sum('total'))['total'] or 0

        # Contamos la cantidad de registros (tickets)
        cantidad_ventas_dia = ventas_de_hoy.count()

        context = {
            # Pasamos los datos reales al contexto
            'ventas_dia': total_ventas_dia, 
            'cantidad_ventas': cantidad_ventas_dia,
            
            'productos_bajos_stock': productos_bajos_stock,
            'lotes_por_vencer': lotes_por_vencer,
            'lotes_vencidos': lotes_vencidos,
            'productos_sin_lotes': productos_sin_lotes,
        }
        return render(request, 'dashboard/dashboard.html', context)
    else:
        return HttpResponseForbidden(f"<h1>Acceso Denegado</h1><p>Tu rol de '{rol_usuario}' no tiene permiso para ver esta página.</p>")