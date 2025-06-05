from django.db import models
from django.contrib.auth import get_user_model

from .documento import Documento

User = get_user_model()

class Comentario(models.Model):
    """
    Comentario hecho por un usuario sobre un documento.
    """
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario por {self.usuario} en {self.documento}"
