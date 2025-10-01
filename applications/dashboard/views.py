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
        return HttpResponseForbidden("<h1>Acceso Denado: No tienes un rol asignado.</h1>")

    rol_usuario = request.user.rol.nombre

    if rol_usuario in ['Administrador', 'Vendedor']:
        
        # --- LÓGICA DE ALERTAS (VERSIÓN FINAL Y ROBUSTA) ---

        # Preparamos la base de la consulta: todos los productos con su stock total calculado
        # Coalesce(..., 0, ...) asegura que si no hay lotes, el stock_total es 0.
        productos_con_stock = Producto.objects.annotate(
            stock_total=Coalesce(Sum('lotes__cantidad_actual'), 0, output_field=DecimalField())
        )

        # Alerta 1: Productos con Stock Bajo (stock > 0 pero <= al mínimo)
        productos_bajos_stock = productos_con_stock.filter(
            stock_total__gt=0,
            stock_total__lte=F('stock_minimo')
        )

        # Alerta 2: Productos sin Stock (stock_total es exactamente 0)
        productos_sin_lotes = productos_con_stock.filter(stock_total=0)
        
        hoy = timezone.now().date()
        proxima_semana = hoy + timedelta(days=7)

        # Alerta 3: Lotes que vencerán pronto
        lotes_por_vencer = Lote.objects.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=proxima_semana
        ).select_related('producto')

        # Alerta 4: Lotes ya vencidos
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