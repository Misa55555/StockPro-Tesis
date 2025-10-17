# applications/cierres/views.py
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count
from django.db import transaction
from django.contrib import messages

from applications.ventas.models import Venta, MetodoPago
from .models import CierreCaja, DetalleCierre

class RealizarCierreView(LoginRequiredMixin, View):
    template_name = 'cierres/realizar_cierre.html'

    def get(self, request, *args, **kwargs):
        # 1. Obtenemos todas las ventas que aún no tienen un cierre asignado
        ventas_pendientes = Venta.objects.filter(cierre__isnull=True)

        # 2. Calculamos el total general y el número de tickets
        total_sistema = ventas_pendientes.aggregate(total=Sum('total'))['total'] or 0
        cantidad_tickets = ventas_pendientes.count()

        # 3. Calculamos los subtotales por cada método de pago
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
        # La lógica para guardar el cierre la implementaremos en el siguiente paso
        # Por ahora, solo redirigimos con un mensaje.
        messages.success(request, "La lógica para guardar el cierre se implementará a continuación.")
        return redirect('cierres_app:realizar_cierre')