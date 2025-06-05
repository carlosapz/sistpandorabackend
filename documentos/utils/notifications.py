import logging
from documentos.models import Notificacion

logger = logging.getLogger(__name__)

def crear_notificacion(usuario, mensaje):
    """
    Crea una notificación para un usuario específico.

    Args:
        usuario: Instancia del usuario que recibirá la notificación.
        mensaje: Texto del mensaje a enviar.

    Returns:
        Notificacion creada o None si hubo error.
    """
    try:
        notificacion = Notificacion.objects.create(
            usuario=usuario,
            mensaje=mensaje
        )
        return notificacion
    except Exception as e:
        logger.error(f"Error al crear la notificación: {str(e)}")
        return None
