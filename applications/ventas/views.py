# applications/ventas/views.py

"""
Módulo de Vistas para la aplicación de Ventas.

Este archivo contiene la lógica de presentación y procesamiento para el módulo
de Punto de Venta (POS). Incluye vistas basadas en clases para la interfaz principal
del POS y funciones auxiliares para operaciones asíncronas (AJAX) como la búsqueda
y creación de clientes.
"""

import json
from decimal import Decimal
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from django.db import models
from django.template.loader import render_to_string

from applications.stock.models import Producto, Lote
from applications.usuarios.forms import ClienteForm
from applications.usuarios.models import Cliente
from .models import MetodoPago, Venta, DetalleVenta

class POSView(LoginRequiredMixin, ListView):
    """
    Vista basada en clase para la interfaz del Punto de Venta (POS).
    
    Gestiona la visualización del catálogo de productos y el procesamiento
    de las transacciones de venta mediante solicitudes AJAX.
    """
    template_name = "ventas/pos.html"
    context_object_name = 'productos'

    def get_queryset(self):
        """
        Define el conjunto de productos disponibles para la venta.
        
        Filtra solo los productos activos y visibles online. Además, anota cada
        producto con su 'stock_total' calculado dinámicamente sumando la cantidad
        actual de sus lotes con stock positivo.
        
        Returns:
            QuerySet: Lista de productos filtrados y anotados con su stock total.
        """
        productos = Producto.objects.filter(
            is_active=True, 
            es_visible_online=True
        ).annotate(
            stock_total=Coalesce(
                Sum('lotes__cantidad_actual', filter=models.Q(lotes__cantidad_actual__gt=0)),
                0,
                output_field=DecimalField()
            )
        )
        return productos

    def get_context_data(self, **kwargs):
        """
        Enriquece el contexto de la plantilla con datos adicionales.
        
        Añade la lista de métodos de pago activos para poblar el selector
        en la interfaz de cobro.
        
        Returns:
            dict: Contexto actualizado para la plantilla.
        """
        context = super().get_context_data(**kwargs)
        context['metodos_pago'] = MetodoPago.objects.filter(is_active=True)
        return context

    def post(self, request, *args, **kwargs):
        """
        Procesa la confirmación de una venta (Checkout).
        
        Este método maneja la solicitud POST enviada al finalizar una venta.
        Realiza las siguientes operaciones críticas dentro de una transacción atómica:
        1. Validación de stock disponible.
        2. Cálculo de totales y aplicación de descuentos.
        3. Creación del registro de Venta.
        4. Descuento de stock siguiendo la estrategia FEFO (First Expired, First Out).
        5. Generación de los registros de detalle de venta.
        
        Args:
            request: La solicitud HTTP conteniendo los datos de la venta en formato JSON.
            
        Returns:
            JsonResponse: Respuesta indicando éxito (con el HTML del ticket) o error.
        """
        data = json.loads(request.body)
        items = data.get('items', {})

        # Recuperación y validación del descuento enviado desde el frontend
        try:
            descuento_input = Decimal(str(data.get('discount', 0)))
            if descuento_input < 0: descuento_input = Decimal('0.00')
        except (ValueError, TypeError):
            descuento_input = Decimal('0.00')

        try:
            with transaction.atomic():
                # --- PASO 1: VALIDACIÓN DE STOCK ---
                # Verifica que exista stock suficiente para todos los ítems antes de proceder.
                for product_id, item_data in items.items():
                    producto = Producto.objects.get(id=product_id)
                    cantidad_solicitada = Decimal(str(item_data['quantity']))
                    
                    stock_total = Lote.objects.filter(
                        producto=producto, 
                        cantidad_actual__gt=0
                    ).aggregate(total=Sum('cantidad_actual'))['total'] or Decimal('0.00')

                    if cantidad_solicitada > stock_total:
                        raise ValueError(f"Stock insuficiente para {producto.nombre}. Solicitado: {cantidad_solicitada}, Disponible: {stock_total}")

                # --- PASO 2: CÁLCULO DE TOTALES Y CREACIÓN DE LA VENTA ---
                metodo_pago = MetodoPago.objects.get(id=data.get('metodoPagoId'))
                cliente = None
                if data.get('clienteId'):
                    cliente = Cliente.objects.get(pk=data.get('clienteId'))

                # Cálculo del subtotal en el backend para garantizar integridad.
                subtotal_calculado = Decimal('0.00')
                for item_data in items.values():
                     subtotal_calculado += Decimal(str(item_data['price'])) * Decimal(str(item_data['quantity']))
                
                # Aplicación del descuento al total calculado.
                total_final = subtotal_calculado - descuento_input
                if total_final < 0: total_final = Decimal('0.00')

                # Persistencia del objeto Venta.
                venta = Venta.objects.create(
                    total=total_final,
                    descuento=descuento_input,
                    metodo_pago=metodo_pago,
                    vendedor=request.user,
                    cliente=cliente,
                )

                # --- PASO 3: PROCESAMIENTO FEFO Y DETALLES DE VENTA ---
                # Itera sobre los productos vendidos para descontar stock y registrar detalles.
                for product_id, item_data in items.items():
                    producto = Producto.objects.get(id=product_id)
                    cantidad_a_vender = Decimal(str(item_data['quantity']))
                    precio_venta_unitario = Decimal(str(item_data['price']))
                    
                    # Selección de lotes ordenada por fecha de vencimiento (FEFO) para rotación de stock.
                    lotes_disponibles = Lote.objects.filter(
                        producto=producto,
                        cantidad_actual__gt=0
                    ).order_by('fecha_vencimiento')

                    costo_total_ponderado = Decimal('0.00')
                    cantidad_inicial_necesaria = cantidad_a_vender
                    
                    # Bucle de descuento de stock sobre los lotes disponibles.
                    for lote in lotes_disponibles:
                        if cantidad_a_vender <= 0: break
                        
                        # Determina la cantidad a tomar del lote actual.
                        cantidad_a_descontar = min(cantidad_a_vender, lote.cantidad_actual)
                        
                        # Actualización del stock del lote.
                        lote.cantidad_actual -= cantidad_a_descontar
                        lote.save()
                        
                        # Acumulación del costo histórico para cálculo de rentabilidad.
                        costo_total_ponderado += cantidad_a_descontar * lote.precio_compra
                        cantidad_a_vender -= cantidad_a_descontar
                    
                    # Cálculo del costo promedio ponderado de las unidades vendidas.
                    precio_compra_promedio = costo_total_ponderado / cantidad_inicial_necesaria

                    # Creación del detalle de venta con información de costos y precios.
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad_inicial_necesaria,
                        precio_unitario_momento=precio_venta_unitario,
                        precio_compra_momento=precio_compra_promedio,
                    )
            
            # Generación del HTML para el modal del ticket de venta.
            modal_html = render_to_string(
                'ventas/partials/ticket_modal.html',
                {'venta': venta}
            )
            return JsonResponse({'status': 'success', 'modal_html': modal_html})

        except (Producto.DoesNotExist, MetodoPago.DoesNotExist, Cliente.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Uno de los componentes de la venta no fue encontrado.'}, status=400)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            # Registro de errores inesperados (log) y respuesta genérica al cliente.
            print(f"Error inesperado en POS: {e}")
            return JsonResponse({'status': 'error', 'message': f'Ocurrió un error inesperado al procesar la venta.'}, status=500)

def buscar_clientes(request):
    """
    Endpoint API para la búsqueda de clientes.
    
    Permite filtrar clientes por nombre o DNI mediante una cadena de búsqueda parcial.
    Retorna los primeros 10 resultados en formato JSON para autocompletado.
    
    Args:
        request: Solicitud GET con el parámetro 'term'.
        
    Returns:
        JsonResponse: Lista de diccionarios con ID y texto descriptivo del cliente.
    """
    term = request.GET.get('term', '')
    clientes = Cliente.objects.filter(
        models.Q(usuario__nombre_completo__icontains=term) | models.Q(dni__icontains=term)
    )[:10]

    results = []
    for cliente in clientes:
        results.append({
            'id': cliente.pk,
            'text': f"{cliente.usuario.nombre_completo} - DNI: {cliente.dni}"
        })
    return JsonResponse(results, safe=False)


def crear_cliente_modal(request):
    """
    Vista para la creación rápida de clientes vía modal (AJAX).
    
    Maneja tanto la renderización del formulario (GET) como su procesamiento (POST).
    Si la creación es exitosa, retorna los datos del nuevo cliente para seleccionarlo
    automáticamente en el POS. Si falla, retorna el formulario con errores.
    
    Args:
        request: Solicitud HTTP.
        
    Returns:
        JsonResponse (POST): Estado de la operación y datos del cliente o HTML del formulario con errores.
        HttpResponse (GET): HTML del formulario de creación.
    """
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'status': 'success',
                'cliente': {
                    'id': cliente.pk,
                    'text': f"{cliente.usuario.nombre_completo} - DNI: {cliente.dni}"
                }
            })
        else:
            form_html = render_to_string('ventas/partials/cliente_form.html', {'form': form}, request=request)
            return JsonResponse({'status': 'error', 'form_html': form_html}, status=400)
    
    form = ClienteForm()
    return render(request, 'ventas/partials/cliente_modal_content.html', {'form': form})