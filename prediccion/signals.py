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

from prediccion.models.tipo_cambio import ModeloTipoCambioConfig
import shutil
import os

@receiver(post_save, sender=ModeloTipoCambioConfig)
def update_modelo_tipo_cambio(sender, instance, **kwargs):
    """
    Cuando se sube un ModeloTipoCambioConfig (desde admin) Y está ACTIVO:
    copia los archivos a la carpeta donde el servicio los usa.
    """
    if instance.activo and instance.tipo_cambio_origen == 'Paralelo':
        modelo_target_path = "modelos_tipo_cambio/lstm_tipo_cambio_paralelo_mejorado.keras"
        csv_target_path = "modelos_tipo_cambio/historico_dolarboliviahoy.csv"

        # Copiar modelo .keras
        if instance.modelo_file and os.path.isfile(instance.modelo_file.path):
            shutil.copy(instance.modelo_file.path, modelo_target_path)
            logger.info(f"✅ Copiado modelo {instance.modelo_file.path} → {modelo_target_path}")
        
        # Copiar CSV
        if instance.csv_dataset_file and os.path.isfile(instance.csv_dataset_file.path):
            shutil.copy(instance.csv_dataset_file.path, csv_target_path)
            logger.info(f"✅ Copiado CSV {instance.csv_dataset_file.path} → {csv_target_path}")

