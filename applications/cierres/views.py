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
    """
    Vista Basada en Clase (CBV) para manejar el proceso de cierre de caja.
    
    - GET: Muestra el resumen de ventas pendientes (total, desglose) y 
      el historial de cierres anteriores.
    - POST: Procesa el formulario de arqueo, crea el CierreCaja y 
      los DetalleCierre correspondientes, y marca las ventas como cerradas.
    """
    
    template_name = 'cierres/realizar_cierre.html'

    def get(self, request, *args, **kwargs):
        """
        Maneja las solicitudes GET. 
        Prepara el contexto con el resumen de ventas pendientes y el historial.
        """
        
        # --- 1. Cálculos para el cierre actual (Ventas Pendientes) ---
        # Selecciona todas las ventas que aún no han sido asignadas a un cierre.
        ventas_pendientes = Venta.objects.filter(cierre__isnull=True)
        
        # Calcula el total monetario de estas ventas. 
        # Si no hay ventas, 'total' sería None, por lo que usamos 'or Decimal'
        total_sistema = ventas_pendientes.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        
        # Cuenta la cantidad de tickets (ventas) individuales.
        cantidad_tickets = ventas_pendientes.count()
        
        # Agrupa las ventas por método de pago y suma sus totales.
        # Esto genera el desglose que se muestra en el formulario.
        desglose_por_metodo = ventas_pendientes.values(
            'metodo_pago__id', 'metodo_pago__nombre'
        ).annotate(
            subtotal=Sum('total')
        ).order_by('metodo_pago__nombre')

        # --- 2. Obtención del Historial de Cierres (NUEVO) ---
        # Se obtiene el historial de todos los cierres de caja realizados.
        # El orden por defecto es '-fecha_cierre' (definido en Meta del modelo).
        #
        # OPTIMIZACIÓN (Tesis): Usamos 'prefetch_related' para evitar 
        # consultas N+1 en la plantilla.
        # - 'usuario': Trae los datos del usuario de cada cierre.
        # - 'detalles': Trae todos los DetalleCierre de cada CierreCaja.
        # - 'detalles__metodo_pago': Trae el MetodoPago de cada DetalleCierre.
        # Esto reduce drásticamente las consultas a la base de datos al renderizar 
        # la tabla de historial y sus detalles desplegables.
        historial_cierres = CierreCaja.objects.prefetch_related(
            'usuario', 
            'detalles', 
            'detalles__metodo_pago'
        ).all()

        # --- 3. Preparación del Contexto para la Plantilla ---
        context = {
            # Datos para el formulario de cierre actual
            'total_sistema': total_sistema,
            'cantidad_tickets': cantidad_tickets,
            'desglose_por_metodo': desglose_por_metodo,
            
            # Datos para la tabla de historial (NUEVO)
            'historial_cierres': historial_cierres,
        }
        
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Maneja las solicitudes POST.
        Valida y guarda el nuevo cierre de caja.
        """
        
        # Usamos una transacción atómica. Si algo falla durante el cierre 
        # (ej. al guardar un detalle), se revierte toda la operación.
        # Esto garantiza la integridad de los datos.
        try:
            with transaction.atomic():
                # 1. Volvemos a obtener las ventas pendientes (bloqueándolas)
                # Se usa 'select_for_update' para bloquear las filas
                # y evitar que otra transacción las modifique (condición de carrera).
                ventas_a_cerrar = Venta.objects.filter(cierre__isnull=True).select_for_update()
                
                if not ventas_a_cerrar.exists():
                    messages.warning(request, "No hay ventas pendientes para cerrar.")
                    return redirect('cierres_app:realizar_cierre')

                # 2. Recalculamos los totales del sistema en el momento del POST
                # Es crucial recalcular esto para asegurar que no hubo ventas
                # entre el GET y el POST.
                total_sistema_final = ventas_a_cerrar.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
                desglose_sistema_final = ventas_a_cerrar.values(
                    'metodo_pago__id'
                ).annotate(
                    subtotal=Sum('total')
                )
                
                # Convertimos el desglose a un diccionario para fácil acceso: {id_metodo: subtotal}
                mapa_subtotales_sistema = {item['metodo_pago__id']: item['subtotal'] for item in desglose_sistema_final}

                # 3. Procesamos los datos del formulario (Arqueo)
                total_arqueo_calculado = Decimal('0.00')
                detalles_para_guardar = []
                
                metodos_pago_con_ventas = MetodoPago.objects.filter(id__in=mapa_subtotales_sistema.keys())

                for metodo in metodos_pago_con_ventas:
                    input_name = f'monto_{metodo.id}'
                    
                    try:
                        # Limpiamos la entrada del usuario (reemplaza coma por punto)
                        monto_contado_str = request.POST.get(input_name, '0').replace(',', '.')
                        monto_contado = Decimal(monto_contado_str if monto_contado_str else '0')
                    except ValueError:
                         messages.error(request, f"Valor inválido ingresado para {metodo.nombre}. Use solo números y punto decimal.")
                         return redirect('cierres_app:realizar_cierre')

                    monto_sistema_metodo = mapa_subtotales_sistema.get(metodo.id, Decimal('0.00'))
                    total_arqueo_calculado += monto_contado
                    
                    # Preparamos el objeto DetalleCierre, pero sin guardarlo
                    # (aún no tenemos el 'cierre' principal)
                    detalles_para_guardar.append(
                        DetalleCierre(
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

                # 5. Asignamos el cierre (ya creado) a los detalles y los guardamos
                for detalle in detalles_para_guardar:
                    detalle.cierre = cierre
                    # Esto podría optimizarse con un 'bulk_create' si 'DetalleCierre'
                    # no tuviera lógica compleja en su 'save()'
                    detalle.save()

                # 6. Marcamos todas las ventas procesadas como parte de este cierre
                # Usamos 'update' para una operación masiva y eficiente.
                ventas_a_cerrar.update(cierre=cierre)

                # 7. Mensaje de éxito
                messages.success(request, f"Cierre de Caja #{cierre.id} realizado exitosamente. Diferencia: ${diferencia_final:+.2f}")
                return redirect('cierres_app:realizar_cierre') 

        except Exception as e:
            # Captura cualquier error inesperado (ej. de base de datos)
            # Gracias a 'transaction.atomic()', la base de datos quedará
            # en un estado consistente (no se habrá cerrado nada).
            messages.error(request, f"Ocurrió un error al intentar cerrar la caja: {str(e)}")
            return redirect('cierres_app:realizar_cierre')