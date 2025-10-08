# applications/dashboard/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, F, Count, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from applications.stock.models import Producto, Lote

@login_required
def dashboard_view(request):
    if not request.user.rol:
        return HttpResponseForbidden("<h1>Acceso Denegado: No tienes un rol asignado.</h1>")

    rol_usuario = request.user.rol.nombre

    if rol_usuario in ['Administrador', 'Vendedor']:
        
        # --- INICIO DE LA CORRECCIÓN ---
        # 1. Primero, obtenemos solo los productos ACTIVOS para las alertas de stock.
        productos_activos = Producto.objects.filter(is_active=True)

        # 2. Construimos la consulta de stock a partir de los productos activos.
        productos_con_stock = productos_activos.annotate(
            stock_total=Coalesce(Sum('lotes__cantidad_actual'), 0, output_field=DecimalField())
        )
        # --- FIN DE LA CORRECCIÓN ---

        # Alerta 1: Productos con Stock Bajo (ahora solo de productos activos)
        productos_bajos_stock = productos_con_stock.filter(
            stock_total__gt=0,
            stock_total__lte=F('stock_minimo')
        )

        # Alerta 2: Productos sin Stock (ahora solo de productos activos)
        productos_sin_lotes = productos_con_stock.filter(stock_total=0)
        
        hoy = timezone.now().date()
        proxima_semana = hoy + timedelta(days=7)

        # Alertas de Vencimiento (estas NO cambian, siguen revisando todos los lotes)
        lotes_por_vencer = Lote.objects.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=proxima_semana
        ).select_related('producto')

        lotes_vencidos = Lote.objects.filter(
            fecha_vencimiento__lt=hoy
        ).select_related('producto')

        context = {
            'ventas_dia': 0,
            'cantidad_ventas': 0,
            'productos_bajos_stock': productos_bajos_stock,
            'lotes_por_vencer': lotes_por_vencer,
            'lotes_vencidos': lotes_vencidos,
            'productos_sin_lotes': productos_sin_lotes,
        }
        return render(request, 'dashboard/dashboard.html', context)
    else:
        return HttpResponseForbidden(f"<h1>Acceso Denegado</h1><p>Tu rol de '{rol_usuario}' no tiene permiso para ver esta página.</p>")