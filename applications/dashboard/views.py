# applications/dashboard/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, F, Count, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
# <--- CAMBIO 1: Importamos datetime y time
from datetime import timedelta, datetime, time

from applications.stock.models import Producto, Lote
# <--- CAMBIO 2: Importamos el modelo Venta
from applications.ventas.models import Venta


@login_required
def dashboard_view(request):
    if not request.user.rol:
        return HttpResponseForbidden("<h1>Acceso Denegado: No tienes un rol asignado.</h1>")

    rol_usuario = request.user.rol.nombre

    if rol_usuario in ['Administrador', 'Vendedor']:

        # --- CAMBIO 3: CÁLCULO DE VENTAS DEL DÍA ---
        hoy = timezone.now().date()
        # Define el rango del día actual (desde 00:00:00 hasta 23:59:59.999999 en el timezone configurado)
        start_of_day = timezone.make_aware(datetime.combine(hoy, time.min))
        end_of_day = timezone.make_aware(datetime.combine(hoy, time.max))

        # Filtra las ventas para el rango de hoy
        ventas_hoy_qs = Venta.objects.filter(
            fecha_hora__range=(start_of_day, end_of_day)
        )

        # Calcula la suma total de las ventas (Venta del Día)
        ventas_dia = ventas_hoy_qs.aggregate(
            total=Coalesce(Sum('total'), 0, output_field=DecimalField())
        )['total']

        # Calcula la cantidad de transacciones (Cant. de Ventas)
        cantidad_ventas = ventas_hoy_qs.count()
        # --- FIN CÁLCULO DE VENTAS DEL DÍA ---

        # 1. Primero, obtenemos solo los productos ACTIVOS para las alertas de stock.
        productos_activos = Producto.objects.filter(is_active=True)

        # 2. Construimos la consulta de stock a partir de los productos activos.
        productos_con_stock = productos_activos.annotate(
            stock_total=Coalesce(Sum('lotes__cantidad_actual'),
                                 0, output_field=DecimalField())
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
            'ventas_dia': ventas_dia,         # <--- Se pasa el valor calculado
            'cantidad_ventas': cantidad_ventas,  # <--- Se pasa el valor calculado
            'productos_bajos_stock': productos_bajos_stock,
            'lotes_por_vencer': lotes_por_vencer,
            'lotes_vencidos': lotes_vencidos,
            'productos_sin_lotes': productos_sin_lotes,
        }
        return render(request, 'dashboard/dashboard.html', context)
    else:
        return HttpResponseForbidden(f"<h1>Acceso Denegado</h1><p>Tu rol de '{rol_usuario}' no tiene permiso para ver esta página.</p>")
