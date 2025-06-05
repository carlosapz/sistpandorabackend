from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notificacion(models.Model):
    """
    Representa una notificación enviada a un usuario.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificaciones")
    mensaje = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje[:20]}"
