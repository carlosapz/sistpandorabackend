from django.db import models
from django.contrib.auth import get_user_model

from .documento import Documento

User = get_user_model()

class VersionDocumento(models.Model):
    """
    Control de versiones de documentos subidos al sistema.
    """
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='versiones')
    archivo = models.FileField(upload_to='documentos/versiones/')
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Versión de {self.documento.titulo} - {self.fecha}"
