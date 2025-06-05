# prediccion/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from prediccion.models.cotizacion import Cotizacion
from prediccion.tasks import generate_cotizacion_pdf

import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Cotizacion)
def launch_pdf_generation(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza una cotización → lanza la tarea de generar PDF.
    """
    if created:
        logger.info(f"🚀 Nueva Cotización ID {instance.id} creada, lanzando tarea generate_cotizacion_pdf")
        generate_cotizacion_pdf.delay(instance.id)
    else:
        logger.info(f"ℹCotización ID {instance.id} actualizada (sin relanzar PDF)")
