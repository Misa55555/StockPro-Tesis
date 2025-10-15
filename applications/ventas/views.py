# applications/ventas/views.py
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
from django.template.loader import render_to_string  # --- CORRECCIÓN 1: IMPORTACIÓN AÑADIDA ---

from applications.stock.models import Producto, Lote
from applications.usuarios.forms import ClienteForm
from applications.usuarios.models import Cliente
from .models import MetodoPago, Venta, DetalleVenta

# applications/ventas/views.py

# ... (todas las importaciones se quedan como están) ...

class POSView(LoginRequiredMixin, ListView):
    template_name = "ventas/pos.html"
    context_object_name = 'productos'

    def get_queryset(self):
        """
        Este método le dice a la ListView qué objetos listar.
        Es el que te estaba faltando.
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
        Este método añade datos extra (como los métodos de pago) a la plantilla.
        """
        context = super().get_context_data(**kwargs)
        context['metodos_pago'] = MetodoPago.objects.filter(is_active=True)
        return context

    def post(self, request, *args, **kwargs):
        """
        Este método maneja la lógica cuando se presiona "PAGAR / COBRAR".
        """
        data = json.loads(request.body)
        items = data.get('items', {})

        try:
            with transaction.atomic():
                # --- PASO 1: VALIDACIÓN DE STOCK ---
                for product_id, item_data in items.items():
                    producto = Producto.objects.get(id=product_id)
                    cantidad_solicitada = Decimal(str(item_data['quantity']))
                    
                    stock_total = Lote.objects.filter(
                        producto=producto, 
                        cantidad_actual__gt=0
                    ).aggregate(total=Sum('cantidad_actual'))['total'] or 0

                    if cantidad_solicitada > stock_total:
                        raise ValueError(f"Stock insuficiente para {producto.nombre}. Solicitado: {cantidad_solicitada}, Disponible: {stock_total}")

                # --- PASO 2: CREACIÓN DE LA VENTA ---
                metodo_pago = MetodoPago.objects.get(id=data.get('metodoPagoId'))
                cliente = None
                if data.get('clienteId'):
                    cliente = Cliente.objects.get(pk=data.get('clienteId'))

                venta = Venta.objects.create(
                    total=Decimal(str(data.get('total'))),
                    metodo_pago=metodo_pago,
                    vendedor=request.user,
                    cliente=cliente,
                )

                # --- PASO 3: PROCESAMIENTO FEFO Y DETALLES DE VENTA ---
                for product_id, item_data in items.items():
                    producto = Producto.objects.get(id=product_id)
                    cantidad_a_vender = Decimal(str(item_data['quantity']))
                    
                    lotes_disponibles = Lote.objects.filter(
                        producto=producto,
                        cantidad_actual__gt=0
                    ).order_by('fecha_vencimiento')

                    costo_total_ponderado = Decimal('0.0')
                    
                    for lote in lotes_disponibles:
                        if cantidad_a_vender <= 0: break
                        cantidad_a_descontar = min(cantidad_a_vender, lote.cantidad_actual)
                        lote.cantidad_actual -= cantidad_a_descontar
                        lote.save()
                        costo_total_ponderado += cantidad_a_descontar * lote.precio_compra
                        cantidad_a_vender -= cantidad_a_descontar
                    
                    precio_compra_promedio = costo_total_ponderado / Decimal(str(item_data['quantity']))

                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=item_data['quantity'],
                        precio_unitario_momento=item_data['price'],
                        precio_compra_momento=precio_compra_promedio,
                    )
            
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
            return JsonResponse({'status': 'error', 'message': f'Ocurrió un error inesperado: {str(e)}'}, status=500)

def buscar_clientes(request):
    term = request.GET.get('term', '')
    clientes = Cliente.objects.filter(
        models.Q(usuario__nombre_completo__icontains=term) | models.Q(dni__icontains=term)
    )[:10]

    results = []
    for cliente in clientes:
        results.append({
            'id': cliente.pk, # Usamos .pk para ser genérico
            'text': f"{cliente.usuario.nombre_completo} - DNI: {cliente.dni}"
        })
    return JsonResponse(results, safe=False)


def crear_cliente_modal(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'status': 'success',
                'cliente': {
                    # --- CORRECCIÓN 2: CAMBIAMOS .id por .pk ---
                    'id': cliente.pk,
                    'text': f"{cliente.usuario.nombre_completo} - DNI: {cliente.dni}"
                }
            })
        else:
            form_html = render_to_string('ventas/partials/cliente_form.html', {'form': form}, request=request)
            return JsonResponse({'status': 'error', 'form_html': form_html}, status=400)
    
    form = ClienteForm()
    return render(request, 'ventas/partials/cliente_modal_content.html', {'form': form})