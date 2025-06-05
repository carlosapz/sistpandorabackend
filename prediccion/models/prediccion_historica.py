from django.db import models # type: ignore
from usuarios.models import Usuario
from prediccion.models.producto import Producto

class PrediccionHistorica(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='predicciones')
    precio_estimado_bs = models.DecimalField(max_digits=12, decimal_places=2)
    precio_estimado_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tipo_cambio_utilizado = models.DecimalField(max_digits=10, decimal_places=4)

    TIPO_CAMBIO_ORIGEN_CHOICES = [("Oficial", "Oficial"), ("Paralelo", "Paralelo")]
    tipo_cambio_origen = models.CharField(max_length=20, choices=TIPO_CAMBIO_ORIGEN_CHOICES, default="Oficial")
    fecha_prediccion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="predicciones_registradas")

    class Meta:
        ordering = ["-fecha_prediccion"]

    def __str__(self) -> str:
        return f"{self.producto.nombre} - {self.precio_estimado_bs} Bs - {self.fecha_prediccion.date()}"
