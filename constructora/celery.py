# constructora/celery.py
import os
from celery import Celery

# Seteamos settings por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'constructora.settings')

# Creamos Celery app
app = Celery('constructora')

# Cargamos config desde Django settings, usando prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover de tasks.py en todas las apps
app.autodiscover_tasks()

# Rutas de colas personalizadas (pdf, ml, low_priority)
app.conf.task_routes = {
    'prediccion.tasks.generate_cotizacion_pdf': {'queue': 'pdf'},
    'prediccion.tasks.predict_price_async': {'queue': 'ml'},
    # Aquí puedes agregar más routes luego
}

# Config defaults extra (retries, timeouts)
app.conf.update(
    task_default_retry_delay=60,      # retry cada 1 minuto
    task_annotations={
        '*': {'rate_limit': '10/s'}   # no saturar (10 tasks por segundo)
    }
)
