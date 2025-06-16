from django.db import models
from usuarios.models import Usuario

class RegistroDolarSistema(models.Model):
    fecha = models.DateField(unique=True)
    tipo_cambio_origen = models.CharField(max_length=20, choices=[("Oficial", "Oficial"), ("Paralelo", "Paralelo")])
    valor = models.DecimalField(max_digits=10, decimal_places=4)

    agregado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fuente = models.CharField(max_length=100, default="Sistema")
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.fecha} - {self.tipo_cambio_origen} - {self.valor}"
