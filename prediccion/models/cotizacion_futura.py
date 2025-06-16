# models/cotizacion_futura.py

from django.db import models
from prediccion.models.cotizacion import Cotizacion
from prediccion.models import Producto

class CotizacionFutura(models.Model):
    cotizacion_original = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name="simulaciones_futuras")
    nombre = models.CharField(max_length=255, default="Simulación futura")
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    dolar_usado = models.FloatField()
    total_bs = models.FloatField()
    productos_simulados = models.JSONField()

    # NUEVOS CAMPOS
    proyecto_nombre = models.CharField(max_length=255, blank=True, null=True)
    categoria_nombre = models.CharField(max_length=255, blank=True, null=True)
    tipo_cambio_origen = models.CharField(max_length=50, default="Paralelo")
    horizonte_dias = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Simulación de {self.cotizacion_original.nombre} ({self.fecha_generacion.date()})"

class ProductoCotizadoFuturo(models.Model):
    cotizacion_futura = models.ForeignKey(CotizacionFutura, related_name="productos_cotizados", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad} uds.)"
