from documentos.models import Notificacion
from rest_framework.exceptions import NotFound


def marcar_notificacion_como_leida(usuario, notificacion_id):
    try:
        notificacion = Notificacion.objects.get(pk=notificacion_id, usuario=usuario)
        notificacion.leido = True
        notificacion.save()
        return {"message": "Notificación marcada como leída."}
    except Notificacion.DoesNotExist:
        raise NotFound("Notificación no encontrada.")


def crear_notificacion(usuario, mensaje):
    """
    Crea una notificación para el usuario con el mensaje dado.
    """
    Notificacion.objects.create(
        usuario=usuario,
        mensaje=mensaje,
        leido=False
    )
