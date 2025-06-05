import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class DocumentosConfig(AppConfig):
    """
    Configuración de la aplicación Documentos.
    Registra señales al iniciar la app para manejar eventos de modelos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'documentos'

    def ready(self):
        """
        Método que se ejecuta al arrancar la aplicación.
        Importa el módulo de señales para registrar handlers.
        """
        try:
            import documentos.signals
        except ImportError as e:
            logger.error(f"Error al importar señales en DocumentosConfig: {e}")
