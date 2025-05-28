from django.apps import AppConfig
import logging

# Configuración de la aplicación de Documentos
class DocumentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'documentos'

    def ready(self):
        # Intentamos importar las señales y configuramos el logger
        try:
            import documentos.signals  # Asegura que las señales se registren al iniciar la app
        except ImportError as e:
            # Log de error detallado para facilitar la depuración
            logger = logging.getLogger(__name__)
            logger.error(f"Error al intentar importar el módulo de señales en 'documentos': {e}")
