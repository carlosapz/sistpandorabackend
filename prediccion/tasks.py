# prediccion/tasks.py

import logging
from celery import shared_task
from prediccion.services.pdf_service import generar_pdf_cotizacion
from prediccion.services.predictor import predecir_precio_actual
from prediccion.models.cotizacion import Cotizacion
from prediccion.models.producto import Producto

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    default_retry_delay=60,
    time_limit=60 * 5,
    queue='pdf'
)
def generate_cotizacion_pdf(self, cotizacion_id):
    """
    Genera PDF de cotización en segundo plano (cola 'pdf').
    """
    try:
        logger.info(f"📄 Generando PDF para Cotización ID {cotizacion_id}")
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        pdf_bytes = generar_pdf_cotizacion(cotizacion)

        # TODO: Guardar el PDF en un modelo o enviarlo por email
        logger.info(f"✅ PDF generado correctamente para Cotización ID {cotizacion_id}")
        return True

    except Cotizacion.DoesNotExist:
        logger.warning(f"⚠️ Cotización ID {cotizacion_id} no encontrada")
        return False

    except Exception as e:
        logger.exception("❌ Error crítico generando PDF, se reintentará...")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    default_retry_delay=60,
    time_limit=60 * 2,
    queue='ml'
)
def predict_price_async(self, producto_id, tipo_cambio_origen="Oficial", tipo_cambio_valor=None):
    """
    Predice precio en segundo plano (cola 'ml').
    """
    try:
        logger.info(f"📊 Prediciendo precio para Producto ID {producto_id}")
        producto = Producto.objects.get(id=producto_id)
        precio = predecir_precio_actual(producto, tipo_cambio_origen, tipo_cambio_valor)

        logger.info(f"✅ Precio estimado para Producto ID {producto_id}: {precio} BOB")
        return precio

    except Producto.DoesNotExist:
        logger.warning(f"⚠️ Producto ID {producto_id} no encontrado")
        return None

    except Exception as e:
        logger.exception("❌ Error crítico en predicción, se reintentará...")
        raise self.retry(exc=e)
