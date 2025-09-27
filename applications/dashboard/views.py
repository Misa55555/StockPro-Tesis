# applications/dashboard/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta

# Importamos los modelos que necesitamos
from applications.stock.models import Producto, Lote

@login_required
def dashboard_view(request):
    if not request.user.rol:
        return HttpResponseForbidden("<h1>Acceso Denegado: No tienes un rol asignado.</h1>")

    rol_usuario = request.user.rol.nombre

    if rol_usuario in ['Administrador', 'Vendedor']:
        # Lógica para Stock Bajo (ya la teníamos)
        productos_bajos_stock = Producto.objects.annotate(
            stock_total=Sum('lotes__cantidad_actual')
        ).filter(
            stock_total__lte=F('stock_minimo')
        )

        # --- INICIO DE LA NUEVA LÓGICA DE VENCIMIENTO ---
        # Calculamos la fecha de hoy y la de dentro de 7 días
        hoy = timezone.now().date()
        proxima_semana = hoy + timedelta(days=7)

        # Buscamos lotes cuya fecha de vencimiento esté en ese rango
        lotes_por_vencer = Lote.objects.filter(
            fecha_vencimiento__range=[hoy, proxima_semana]
        )
        # --- FIN DE LA NUEVA LÓGICA DE VENCIMIENTO ---

        context = {
            'ventas_dia': 0,
            'cantidad_ventas': 0,
            'productos_bajos_stock': productos_bajos_stock,
            'lotes_por_vencer': lotes_por_vencer, # Pasamos la nueva lista a la plantilla
        }
        return render(request, 'dashboard/dashboard.html', context)
    else:
        return HttpResponseForbidden(f"<h1>Acceso Denegado</h1><p>Tu rol de '{rol_usuario}' no tiene permiso para ver esta página.</p>")