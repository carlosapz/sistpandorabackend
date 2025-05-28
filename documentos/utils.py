import logging

from .models import Notificacion

def crear_notificacion(usuario, mensaje):
    """
    Crea una notificación para un usuario específico.
    
    Parámetros:
    - usuario: Usuario al que se le enviará la notificación.
    - mensaje: El contenido de la notificación.
    """
    try:
        # Crear la notificación
        notificacion = Notificacion.objects.create(
            usuario=usuario,
            mensaje=mensaje
        )
        return notificacion
    except Exception as e:
        # Registrar cualquier error en la creación de la notificación
        logger = logging.getLogger(__name__)
        logger.error(f"Error al crear la notificación: {str(e)}")
        return None
