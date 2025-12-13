# applications/cierres/admin.py

"""
Módulo de configuración del Panel de Administración para la aplicación 'cierres'.

Este archivo define la representación y comportamiento de los modelos `CierreCaja`
y `DetalleCierre` dentro de la interfaz administrativa de Django.
La configuración se centra en la auditoría y la integridad de los datos,
restringiendo las capacidades de modificación manual para garantizar que los registros
de cierre de caja sean inmutables y reflejen fielmente las operaciones realizadas
a través de la lógica de negocio.
"""

from django.contrib import admin
from .models import CierreCaja, DetalleCierre

class DetalleCierreInline(admin.TabularInline):
    """
    Configuración de vista en línea (Inline) para el modelo DetalleCierre.

    Esta clase permite visualizar los detalles financieros desglosados por método de pago
    directamente dentro de la ficha de administración del modelo padre `CierreCaja`.
    Se configura en modo de solo lectura para preservar la integridad del arqueo registrado.
    """
    model = DetalleCierre
    extra = 0 # Evita la visualización de formularios vacíos adicionales para nuevos registros.
    
    # Define los campos que se mostrarán en modo de solo lectura para evitar ediciones accidentales o malintencionadas.
    readonly_fields = ('metodo_pago', 'monto_sistema', 'monto_arqueo', 'diferencia') 
    
    # Deshabilita la capacidad de eliminar detalles individuales para mantener la consistencia del cierre global.
    can_delete = False 

    def has_add_permission(self, request, obj=None):
        """
        Restringe la adición manual de detalles de cierre desde el panel de administración.
        Los detalles deben generarse exclusivamente durante el proceso de cierre de caja.
        """
        return False 

@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para el modelo CierreCaja.

    Define las columnas visibles en el listado, los filtros disponibles y los campos de búsqueda.
    Establece restricciones estrictas sobre la creación, edición y eliminación de registros
    para asegurar que el historial de cierres actúe como una fuente de verdad inalterable.
    """
    # Campos a mostrar en la lista de registros para facilitar la identificación y auditoría rápida.
    list_display = ('id', 'fecha_cierre', 'usuario', 'total_sistema', 'total_arqueo', 'diferencia')
    
    # Filtros laterales para segmentar los datos por fecha y responsable.
    list_filter = ('fecha_cierre', 'usuario')
    
    # Habilita la búsqueda por ID de cierre y nombre de usuario.
    search_fields = ('id', 'usuario__username')
    
    # Establece todos los campos informativos como de solo lectura en la vista de detalle.
    readonly_fields = ('fecha_cierre', 'usuario', 'total_sistema', 'total_arqueo', 'diferencia') 
    
    # Integra la visualización de los detalles (DetalleCierre) dentro de este modelo.
    inlines = [DetalleCierreInline] 

    def has_add_permission(self, request):
        """
        Deshabilita la creación manual de registros de Cierre de Caja desde el administrador.
        La creación debe ocurrir únicamente a través de la vista de negocio 'RealizarCierreView'.
        """
        return False 

    def has_delete_permission(self, request, obj=None):
        """
        Deshabilita la eliminación de registros de Cierre de Caja.
        
        Esta restricción es fundamental para garantizar la persistencia histórica y la
        trazabilidad de las operaciones financieras, impidiendo el borrado de evidencia de arqueos.
        """
        return False