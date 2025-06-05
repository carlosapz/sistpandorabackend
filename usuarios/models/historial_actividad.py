from django.db import models
from django.conf import settings

class HistorialActividad(models.Model):
    """
    Guarda el historial de actividades del usuario en el sistema.
    """
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accion = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion}"
