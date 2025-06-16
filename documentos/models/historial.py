from django.db import models
from django.contrib.auth import get_user_model
from .documento import Documento

User = get_user_model()

class HistorialActividad(models.Model):
    ACCIONES = [
        ('CREACION', 'Creación'),
        ('EDICION', 'Edición'),
        ('ELIMINACION', 'Eliminación'),
        ('APROBACION', 'Aprobación'),
        ('RECHAZO', 'Rechazo'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actividades'
    )
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,  # 💥 Cambiado a CASCADE para que se borre con el documento
        related_name="historiales"
    )

    accion = models.CharField(max_length=20, choices=ACCIONES)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accion} por {self.usuario} en {self.fecha}"


class ReporteHistorial(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    filtros_aplicados = models.TextField()
    tipo_reporte = models.CharField(max_length=10, default="PDF")

    def __str__(self):
        return f"Reporte generado por {self.usuario} el {self.fecha_generacion}"
