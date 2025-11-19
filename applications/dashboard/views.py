# applications/dashboard/views.py

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
    if not request.user.rol:
        return HttpResponseForbidden("<h1>Acceso Denegado: No tienes un rol asignado.</h1>")

    rol_usuario = request.user.rol.nombre

    if rol_usuario in ['Administrador', 'Vendedor']:
        
        # --- 1. LÓGICA DE STOCK (Alertas) ---
        productos_activos = Producto.objects.filter(is_active=True)

        productos_con_stock = productos_activos.annotate(
            stock_total=Coalesce(Sum('lotes__cantidad_actual'), 0, output_field=DecimalField())
        )

        # Alerta 1: Productos con Stock Bajo
        productos_bajos_stock = productos_con_stock.filter(
            stock_total__gt=0,
            stock_total__lte=F('stock_minimo')
        )

        # Alerta 2: Productos sin Stock
        productos_sin_lotes = productos_con_stock.filter(stock_total=0)
        
        hoy = timezone.now().date()
        proxima_semana = hoy + timedelta(days=7)

        # Alertas de Vencimiento
        lotes_por_vencer = Lote.objects.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=proxima_semana,
            cantidad_actual__gt=0  # Solo lotes que aún tengan stock
        ).select_related('producto')

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