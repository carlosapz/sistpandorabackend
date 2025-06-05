# documentos/services/historial_service.py

from documentos.models import HistorialActividad

def registrar_historial(usuario, documento=None, accion=None):
    """
    Registra una actividad en el historial.
    """
    HistorialActividad.objects.create(
        usuario=usuario,
        documento=documento,
        accion=accion
    )
