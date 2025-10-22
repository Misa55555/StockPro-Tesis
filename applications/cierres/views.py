# applications/cierres/views.py
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, F # Asegúrate de importar F
from django.db import transaction
from django.contrib import messages
from django.utils import timezone # Para la fecha/hora actual
from decimal import Decimal # Para manejar los montos

from applications.ventas.models import Venta, MetodoPago
from .models import CierreCaja, DetalleCierre

class RealizarCierreView(LoginRequiredMixin, View):
    template_name = 'cierres/realizar_cierre.html'

    def get(self, request, *args, **kwargs):
        ventas_pendientes = Venta.objects.filter(cierre__isnull=True)
        total_sistema = ventas_pendientes.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        cantidad_tickets = ventas_pendientes.count()
        desglose_por_metodo = ventas_pendientes.values(
            'metodo_pago__id', 'metodo_pago__nombre'
        ).annotate(
            subtotal=Sum('total')
        ).order_by('metodo_pago__nombre')

        context = {
            'total_sistema': total_sistema,
            'cantidad_tickets': cantidad_tickets,
            'desglose_por_metodo': desglose_por_metodo,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Usamos una transacción atómica para asegurar que todo se guarde o nada
        try:
            with transaction.atomic():
                # 1. Volvemos a obtener las ventas pendientes justo antes de cerrar
                ventas_a_cerrar = Venta.objects.filter(cierre__isnull=True)
                
                if not ventas_a_cerrar.exists():
                    messages.warning(request, "No hay ventas pendientes para cerrar.")
                    return redirect('cierres_app:realizar_cierre')

                # 2. Calculamos los totales del sistema DE NUEVO
                total_sistema_final = ventas_a_cerrar.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
                desglose_sistema_final = ventas_a_cerrar.values(
                    'metodo_pago__id'
                ).annotate(
                    subtotal=Sum('total')
                )
                
                # Convertimos el desglose a un diccionario para fácil acceso: {metodo_pago_id: subtotal}
                mapa_subtotales_sistema = {item['metodo_pago__id']: item['subtotal'] for item in desglose_sistema_final}

                # 3. Procesamos los datos del formulario (arqueo)
                total_arqueo_calculado = Decimal('0.00')
                detalles_para_guardar = []
                
                # Iteramos sobre los métodos de pago que SÍ tuvieron ventas
                metodos_pago_con_ventas = MetodoPago.objects.filter(id__in=mapa_subtotales_sistema.keys())

                for metodo in metodos_pago_con_ventas:
                    # El nombre del input en el form es 'monto_{id_metodo_pago}'
                    input_name = f'monto_{metodo.id}'
                    # Obtenemos el valor del POST, asegurándonos de que sea un Decimal válido
                    try:
                        monto_contado_str = request.POST.get(input_name, '0').replace(',', '.') # Reemplazar comas por puntos
                        monto_contado = Decimal(monto_contado_str if monto_contado_str else '0')
                    except ValueError:
                         messages.error(request, f"Valor inválido ingresado para {metodo.nombre}. Use solo números y punto decimal.")
                         return redirect('cierres_app:realizar_cierre')

                    monto_sistema_metodo = mapa_subtotales_sistema.get(metodo.id, Decimal('0.00'))
                    total_arqueo_calculado += monto_contado
                    
                    detalles_para_guardar.append(
                        DetalleCierre(
                            # Aún no tenemos el ID del cierre, lo asignaremos después
                            metodo_pago=metodo,
                            monto_sistema=monto_sistema_metodo,
                            monto_arqueo=monto_contado
                        )
                    )

                # 4. Creamos el registro principal del Cierre de Caja
                diferencia_final = total_arqueo_calculado - total_sistema_final
                
                cierre = CierreCaja.objects.create(
                    usuario=request.user,
                    total_sistema=total_sistema_final,
                    total_arqueo=total_arqueo_calculado,
                    diferencia=diferencia_final,
                    observaciones=request.POST.get('observaciones', '')
                )

                # 5. Asignamos el cierre a los detalles y los guardamos
                for detalle in detalles_para_guardar:
                    detalle.cierre = cierre
                    detalle.save()

                # 6. Marcamos todas las ventas procesadas como parte de este cierre
                ventas_a_cerrar.update(cierre=cierre)

                # 7. Mensaje de éxito
                messages.success(request, f"Cierre de Caja #{cierre.id} realizado exitosamente. Diferencia: ${diferencia_final:+.2f}")
                # Podríamos redirigir al historial aquí en el futuro
                return redirect('cierres_app:realizar_cierre') 

        except Exception as e:
            messages.error(request, f"Ocurrió un error al intentar cerrar la caja: {str(e)}")
            return redirect('cierres_app:realizar_cierre')