# applications/cierres/views.py

"""
Módulo de Vistas para la gestión de Cierres de Caja.

Este archivo contiene la lógica de negocio necesaria para controlar el ciclo de vida
del cierre de caja. Gestiona la presentación de la interfaz de usuario (para arqueo
y consulta de historial) y el procesamiento de la lógica de cierre, incluyendo el cálculo
de totales, la validación de montos ingresados y la actualización de estados de ventas.
"""

from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, F 
from django.db import transaction
from django.contrib import messages
from django.utils import timezone 
from decimal import Decimal 

from applications.ventas.models import Venta, MetodoPago
from .models import CierreCaja, DetalleCierre

class RealizarCierreView(LoginRequiredMixin, View):
    """
    Vista basada en clases (CBV) para administrar el proceso de cierre de caja.

    Esta vista maneja dos operaciones principales:
    1. GET: Renderiza la pantalla de cierre, mostrando un resumen financiero preliminar
       de las ventas pendientes y el historial de cierres previos.
    2. POST: Procesa el formulario de arqueo enviado por el usuario, valida la información,
       ejecuta la transacción de cierre y actualiza los registros correspondientes.
    """
    
    template_name = 'cierres/realizar_cierre.html'

    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud HTTP GET.
        
        Calcula en tiempo real los totales de las ventas que aún no han sido cerradas
        para asistir al usuario en el proceso de arqueo físico. También recupera el
        historial de cierres para auditoría visual.
        
        Args:
            request: El objeto HttpRequest.
            
        Returns:
            HttpResponse: La plantilla renderizada con el contexto financiero y el historial.
        """
        
        # --- 1. Cálculos para el cierre actual (Ventas Pendientes) ---
        # Filtra las ventas que no tienen asignado un objeto CierreCaja (pendientes).
        ventas_pendientes = Venta.objects.filter(cierre__isnull=True)
        
        # Calcula la suma total de los importes de venta. Si no hay ventas, retorna 0.00.
        total_sistema = ventas_pendientes.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        
        # Obtiene el conteo total de transacciones (tickets) pendientes.
        cantidad_tickets = ventas_pendientes.count()
        
        # Genera un desglose agrupado por método de pago para comparar contra el arqueo físico.
        desglose_por_metodo = ventas_pendientes.values(
            'metodo_pago__id', 'metodo_pago__nombre'
        ).annotate(
            subtotal=Sum('total')
        ).order_by('metodo_pago__nombre')

        # --- 2. Obtención del Historial de Cierres ---
        # Recupera los registros históricos de cierres anteriores.
        # Utiliza 'prefetch_related' para realizar una carga optimizada (Eager Loading) de
        # las relaciones (usuario, detalles, ventas, etc.), reduciendo el número de consultas SQL.
        historial_cierres = CierreCaja.objects.prefetch_related(
            'usuario', 
            'detalles', 
            'detalles__metodo_pago',
            'ventas_incluidas',                
            'ventas_incluidas__vendedor',      
            'ventas_incluidas__metodo_pago',    
        ).all()

        # --- 3. Preparación del Contexto ---
        context = {
            'total_sistema': total_sistema,
            'cantidad_tickets': cantidad_tickets,
            'desglose_por_metodo': desglose_por_metodo,
            'historial_cierres': historial_cierres,
        }
        
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Maneja la solicitud HTTP POST para ejecutar el cierre de caja.
        
        Implementa una transacción atómica para garantizar la integridad referencial y financiera.
        Bloquea las ventas pendientes para evitar condiciones de carrera, valida los montos
        ingresados y persiste el cierre junto con sus detalles.
        
        Args:
            request: El objeto HttpRequest con los datos del formulario.
            
        Returns:
            HttpResponseRedirect: Redirecciona a la misma vista tras el procesamiento exitoso o fallido.
        """
        
        try:
            # Inicio del bloque transaccional atómico.
            with transaction.atomic():
                # 1. Bloqueo y recuperación de ventas pendientes.
                # 'select_for_update' bloquea las filas seleccionadas hasta que termine la transacción,
                # previniendo modificaciones concurrentes durante el cierre.
                ventas_a_cerrar = Venta.objects.filter(cierre__isnull=True).select_for_update()
                
                if not ventas_a_cerrar.exists():
                    messages.warning(request, "No hay ventas pendientes para cerrar.")
                    return redirect('cierres_app:realizar_cierre')

                # 2. Recálculo de totales del sistema (Snapshot).
                # Es crítico recalcular aquí para asegurar que los totales coincidan exactamente
                # con los registros bloqueados en este instante.
                total_sistema_final = ventas_a_cerrar.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
                desglose_sistema_final = ventas_a_cerrar.values(
                    'metodo_pago__id'
                ).annotate(
                    subtotal=Sum('total')
                )
                
                # Crea un mapa hash para acceso rápido O(1) a los subtotales del sistema durante la iteración.
                mapa_subtotales_sistema = {item['metodo_pago__id']: item['subtotal'] for item in desglose_sistema_final}

                # 3. Procesamiento de datos del formulario (Arqueo).
                total_arqueo_calculado = Decimal('0.00')
                detalles_para_guardar = []
                
                # Identifica los métodos de pago relevantes para este cierre.
                metodos_pago_con_ventas = MetodoPago.objects.filter(id__in=mapa_subtotales_sistema.keys())

                for metodo in metodos_pago_con_ventas:
                    input_name = f'monto_{metodo.id}'
                    
                    try:
                        # Normalización de entrada: convierte comas a puntos y parsea a Decimal.
                        monto_contado_str = request.POST.get(input_name, '0').replace(',', '.')
                        monto_contado = Decimal(monto_contado_str if monto_contado_str else '0')
                    except ValueError:
                         messages.error(request, f"Valor inválido ingresado para {metodo.nombre}. Use solo números y punto decimal.")
                         return redirect('cierres_app:realizar_cierre')

                    monto_sistema_metodo = mapa_subtotales_sistema.get(metodo.id, Decimal('0.00'))
                    total_arqueo_calculado += monto_contado
                    
                    # Instanciación en memoria de los detalles del cierre.
                    detalles_para_guardar.append(
                        DetalleCierre(
                            metodo_pago=metodo,
                            monto_sistema=monto_sistema_metodo,
                            monto_arqueo=monto_contado
                        )
                    )

                # 4. Creación y persistencia del objeto maestro CierreCaja.
                diferencia_final = total_arqueo_calculado - total_sistema_final
                
                cierre = CierreCaja.objects.create(
                    usuario=request.user,
                    total_sistema=total_sistema_final,
                    total_arqueo=total_arqueo_calculado,
                    diferencia=diferencia_final,
                    observaciones=request.POST.get('observaciones', '')
                )

                # 5. Asociación y persistencia de los detalles.
                for detalle in detalles_para_guardar:
                    detalle.cierre = cierre
                    detalle.save()

                # 6. Actualización masiva (Bulk Update) de las ventas.
                # Vincula las ventas procesadas con el ID del nuevo cierre.
                ventas_a_cerrar.update(cierre=cierre)

                # 7. Finalización exitosa.
                messages.success(request, f"Cierre de Caja #{cierre.id} realizado exitosamente. Diferencia: ${diferencia_final:+.2f}")
                return redirect('cierres_app:realizar_cierre') 

        except Exception as e:
            # Manejo de excepciones generales.
            # Gracias a 'transaction.atomic()', cualquier error revierte todos los cambios en BD.
            messages.error(request, f"Ocurrió un error al intentar cerrar la caja: {str(e)}")
            return redirect('cierres_app:realizar_cierre')