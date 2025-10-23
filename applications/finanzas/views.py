# applications/finanzas/views.py
import json
from datetime import datetime, date, time
from django.utils import timezone
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Sum, F, Count, DecimalField
from django.db.models.functions import TruncMonth, TruncDay, Coalesce
from django.conf import settings # <-- ¡NUEVO!

from applications.ventas.models import Venta, DetalleVenta
from applications.stock.models import Categoria as CategoriaProducto, Producto
from .models import Gasto, CategoriaGasto
from .forms import GastoForm, CategoriaGastoForm

# VISTA 1: La que renderiza el HTML (Sin cambios)
# ------------------------------------------------
class DashboardFinanzasView(LoginRequiredMixin, TemplateView):
    template_name = 'finanzas/dashboard.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Dashboard Financiero'
        today = timezone.now().date()
        context['fecha_hoy'] = today
        context['fecha_inicio_mes'] = today.replace(day=1)
        context['gasto_form'] = GastoForm()
        context['categoria_gasto_form'] = CategoriaGastoForm()
        return context


# VISTA 2: La que provee los datos (JSON) (¡¡MODIFICADA!!)
# ------------------------------------------------
class FinanzasDataJSONView(LoginRequiredMixin, View):
    """
    API Endpoint que devuelve un JSON con todos los datos calculados
    para que Chart.js pueda dibujar los gráficos.
    """
    
    def get(self, request, *args, **kwargs):
        
        # --- 1. Obtener y validar el rango de fechas ---
        try:
            today = timezone.now().date()
            start_date_str = request.GET.get('start', today.replace(day=1).strftime('%Y-%m-%d'))
            end_date_str = request.GET.get('end', today.strftime('%Y-%m-%d'))
            
            start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            start_date_for_gasto = start_date_obj
            end_date_for_gasto = end_date_obj
            
            start_dt_naive = datetime.combine(start_date_obj, time.min)
            end_dt_naive = datetime.combine(end_date_obj, time.max)

            start_date_aware = timezone.make_aware(start_dt_naive, timezone.get_current_timezone())
            end_date_aware = timezone.make_aware(end_dt_naive, timezone.get_current_timezone())

        except ValueError:
            return JsonResponse({'error': 'Formato de fecha inválido. Usar YYYY-MM-DD.'}, status=400)

        # --- 2. Calcular los KPIs Principales ---
        
        total_ingresos = Venta.objects.filter(
            fecha_hora__range=[start_date_aware, end_date_aware]
        ).aggregate(total=Sum('total'))['total'] or 0

        total_cogs = DetalleVenta.objects.filter(
            venta__fecha_hora__range=[start_date_aware, end_date_aware]
        ).aggregate(total=Sum(F('cantidad') * F('precio_compra_momento')))['total'] or 0

        total_gastos = Gasto.objects.filter(
            fecha_imputacion__range=[start_date_for_gasto, end_date_for_gasto]
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        ganancia_bruta = total_ingresos - total_cogs
        beneficio_neto = ganancia_bruta - total_gastos

        # --- 3. Preparar datos para los Gráficos de Torta y Líneas ---

        # (Gráfico Gastos por Categoría)
        gastos_por_categoria_qs = CategoriaGasto.objects.filter(
            gasto__fecha_imputacion__range=[start_date_for_gasto, end_date_for_gasto]
        ).annotate(total=Sum('gasto__monto')).order_by('-total')

        chart_gastos_categoria = {
            'labels': [g.nombre for g in gastos_por_categoria_qs if g.total > 0],
            'data': [g.total for g in gastos_por_categoria_qs if g.total > 0],
        }

        # (Gráfico Ventas por Categoría de Producto)
        ventas_por_categoria_qs = CategoriaProducto.objects.filter(
            productos__detalleventa__venta__fecha_hora__range=[start_date_aware, end_date_aware]
        ).annotate(total_vendido=Sum('productos__detalleventa__subtotal')).order_by('-total_vendido')
        
        chart_ventas_categoria = {
            'labels': [c.nombre for c in ventas_por_categoria_qs if c.total_vendido > 0],
            'data': [c.total_vendido for c in ventas_por_categoria_qs if c.total_vendido > 0],
        }

        # (Gráfico Evolución de Ganancias)
        ingresos_por_dia = Venta.objects.filter(
            fecha_hora__range=[start_date_aware, end_date_aware]
        ).annotate(dia=TruncDay('fecha_hora')).values('dia').annotate(total=Sum('total')).order_by('dia')
        
        gastos_por_dia = Gasto.objects.filter(
            fecha_imputacion__range=[start_date_for_gasto, end_date_for_gasto]
        ).annotate(dia=TruncDay('fecha_imputacion')).values('dia').annotate(total=Sum('monto')).order_by('dia')
        
        ingresos_map = {d['dia'].strftime('%Y-%m-%d'): d['total'] for d in ingresos_por_dia}
        gastos_map = {d['dia'].strftime('%Y-%m-%d'): d['total'] for d in gastos_por_dia}
        
        all_labels = sorted(list(set(ingresos_map.keys()) | set(gastos_map.keys())))
        
        chart_evolucion = {
            'labels': all_labels,
            'ingresos_data': [ingresos_map.get(label, 0) for label in all_labels],
            'gastos_data': [gastos_map.get(label, 0) for label in all_labels],
        }

        # --- 4. ¡NUEVO! Cálculos para Rankings (Paso 2) ---

        # Base de detalles de venta en el rango
        detalles_en_rango = DetalleVenta.objects.filter(
            venta__fecha_hora__range=[start_date_aware, end_date_aware]
        ).select_related('producto')

        # Ranking 1: Top 5 Productos (Más Vendidos por Cantidad)
        top_productos_venta_qs = detalles_en_rango.values(
            'producto__nombre' # Agrupamos por nombre
        ).annotate(
            total_cantidad=Sum('cantidad') # Sumamos las cantidades
        ).order_by('-total_cantidad')[:5] # Ordenamos y tomamos los 5 primeros

        chart_top_productos_venta = {
            'labels': [p['producto__nombre'] for p in top_productos_venta_qs],
            'data': [p['total_cantidad'] for p in top_productos_venta_qs],
        }

        # Ranking 2: Top 5 Productos (Más Rentables)
        top_productos_rentables_qs = detalles_en_rango.annotate(
            # Calculamos la ganancia de *cada* detalle de venta
            ganancia_linea=F('subtotal') - (F('cantidad') * F('precio_compra_momento'))
        ).values(
            'producto__nombre' # Agrupamos por nombre
        ).annotate(
            ganancia_total=Sum('ganancia_linea') # Sumamos las ganancias
        ).order_by('-ganancia_total')[:5] # Ordenamos y tomamos los 5 primeros

        chart_top_productos_rentables = {
            'labels': [p['producto__nombre'] for p in top_productos_rentables_qs],
            'data': [p['ganancia_total'] for p in top_productos_rentables_qs],
        }

        # Ranking 3: Ventas por Vendedor
        ventas_por_vendedor_qs = Venta.objects.filter(
            fecha_hora__range=[start_date_aware, end_date_aware]
        ).values(
            'vendedor__username' # Agrupamos por username
        ).annotate(
            total_vendido=Sum('total')
        ).order_by('-total_vendido')

        chart_ventas_vendedor = {
            'labels': [v['vendedor__username'] or 'Sin Vendedor' for v in ventas_por_vendedor_qs],
            'data': [v['total_vendido'] for v in ventas_por_vendedor_qs],
        }


        # --- 5. Construir la respuesta JSON ---
        data = {
            'kpis': {
                'total_ingresos': total_ingresos,
                'total_cogs': total_cogs,
                'ganancia_bruta': ganancia_bruta,
                'total_gastos': total_gastos,
                'beneficio_neto': beneficio_neto,
            },
            'charts': {
                'gastos_por_categoria': chart_gastos_categoria,
                'ventas_por_categoria': chart_ventas_categoria,
                'evolucion_ingresos_gastos': chart_evolucion,
                
                # ¡Nuevos datos añadidos!
                'top_productos_venta': chart_top_productos_venta,
                'top_productos_rentables': chart_top_productos_rentables,
                'ventas_por_vendedor': chart_ventas_vendedor,
            }
        }
        
        return JsonResponse(data)


# VISTA 3: La que guarda el gasto (Sin cambios)
# ------------------------------------------------
class RegistrarGastoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = GastoForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.usuario_registra = request.user
            gasto.save()
            return JsonResponse({'success': True, 'gasto_id': gasto.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)

# VISTA 4: La que guarda la categoría (Sin cambios)
# ------------------------------------------------
class RegistrarCategoriaGastoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = CategoriaGastoForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            return JsonResponse({
                'success': True, 
                'categoria_id': categoria.id,
                'categoria_nombre': categoria.nombre,
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)