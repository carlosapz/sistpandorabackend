"""
Configuración de la aplicación Predicción.
Define nombre, tipo de auto field y hook para señales.
"""

from django.apps import AppConfig

class PrediccionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prediccion'

    def ready(self):
        """
        Hook para inicialización de señales o lógica al iniciar la app.
        """
        # from . import signals  # Descomenta si tienes signals.py
        pass

class PrediccionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prediccion'

    def ready(self):
        import prediccion.signals
