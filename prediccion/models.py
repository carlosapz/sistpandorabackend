from django.db import models
from usuarios.models import Usuario
from documentos.models import Proyecto, Categoria
from .utils import obtener_precio_dolar, obtener_dolar_paralelo
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal, InvalidOperation

def obtener_fecha_validez():
    return timezone.now() + timedelta(weeks=1)

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    unidad_medida = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    modelo_lstm = models.FileField(upload_to='modelos_lstm/')
    csv_datos = models.FileField(upload_to='datasets_productos/')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Cotizacion(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='cotizaciones'
    )
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name='cotizaciones'
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name='cotizaciones', default=1
    )
    nombre = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    total_general = models.DecimalField(max_digits=15, decimal_places=2)

    fecha_prediccion = models.DateTimeField(auto_now=True)
    fecha_validez = models.DateTimeField(default=obtener_fecha_validez)
    tipo_cambio_dolar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    tipo_cambio_origen = models.CharField(
        max_length=20,
        choices=[("Oficial", "Oficial"), ("Paralelo", "Paralelo")],
        default="Oficial"
    )
    tipo_cambio_valor = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    def es_valida(self):
        tipo_cambio_actual = obtener_dolar_paralelo() if self.tipo_cambio_origen == "Paralelo" else obtener_precio_dolar()
        if tipo_cambio_actual is None or self.tipo_cambio_dolar is None:
            return False
        try:
            actual = Decimal(str(tipo_cambio_actual))
            guardado = Decimal(str(self.tipo_cambio_dolar))
            diferencia = abs(guardado - actual) / guardado
            return diferencia <= Decimal("0.05")
        except:
            return False

class ProductoCotizado(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion, on_delete=models.CASCADE, related_name='productos_cotizados'
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} unidades - Cotización #{self.cotizacion.id}'

class PrediccionHistorica(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='predicciones')
    precio_estimado_bs = models.DecimalField(max_digits=12, decimal_places=2)
    precio_estimado_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tipo_cambio_utilizado = models.DecimalField(max_digits=10, decimal_places=4)
    tipo_cambio_origen = models.CharField(
        max_length=20,
        choices=[("Oficial", "Oficial"), ("Paralelo", "Paralelo")],
        default="Oficial"
    )
    fecha_prediccion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="predicciones_registradas"
    )

    class Meta:
        ordering = ["-fecha_prediccion"]

    def __str__(self):
        return f"{self.producto.nombre} - {self.precio_estimado_bs} Bs - {self.fecha_prediccion.date()}"
