import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from documentos.models import HistorialActividad, Documento

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Documento)
def registrar_historial_guardado(sender, instance, created, **kwargs):
    """
    Registra una entrada en el historial cuando se crea o edita un documento.
    Solo se ejecuta tras confirmar que la transacción fue exitosa.
    """
    def _registrar():
        try:
            accion = 'CREACION' if created else 'EDICION'
            HistorialActividad.objects.create(
                usuario=instance.usuario,
                documento=instance,
                accion=accion
            )
        except Exception as e:
            logger.error(f"Error al registrar historial de documento: {e}")

    transaction.on_commit(_registrar)

@receiver(post_delete, sender=Documento)
def registrar_historial_eliminacion(sender, instance, **kwargs):
    """
    Registra una entrada en el historial cuando se elimina un documento.
    """
    try:
        HistorialActividad.objects.create(
            usuario=instance.usuario,
            documento=instance,
            accion='ELIMINACION'
        )
    except Exception as e:
        logger.error(f"Error al registrar historial de eliminación: {e}")
