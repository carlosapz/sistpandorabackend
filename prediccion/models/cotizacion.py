from django.db import models
from usuarios.models import Usuario
from documentos.models import Proyecto, Categoria, Obra
from prediccion.models.producto import Producto
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from typing import Optional
from prediccion.services.cotizacion_service import es_valida_cotizacion

def obtener_fecha_validez() -> timezone.datetime:
    return timezone.now() + timedelta(weeks=1)

class Cotizacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cotizaciones')

    # NUEVO: Obra vinculada a la cotización
    obra = models.ForeignKey(
        Obra,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cotizaciones'
    )

    # Se mantienen estos campos por compatibilidad
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='cotizaciones')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='cotizaciones', default=1)

    nombre = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_prediccion = models.DateTimeField(auto_now=True)
    fecha_validez = models.DateTimeField(default=obtener_fecha_validez)

    tipo_cambio_dolar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    TIPO_CAMBIO_ORIGEN_CHOICES = [("Oficial", "Oficial"), ("Paralelo", "Paralelo")]
    tipo_cambio_origen = models.CharField(max_length=20, choices=TIPO_CAMBIO_ORIGEN_CHOICES, default="Oficial")
    tipo_cambio_valor = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    # NUEVOS CAMPOS FINANCIEROS
    gastos_generales = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    utilidad = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    contingencia = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    total_general = models.DecimalField(max_digits=15, decimal_places=2)

    def es_valida(self) -> bool:
        return es_valida_cotizacion(self.tipo_cambio_origen, self.tipo_cambio_dolar)

    def __str__(self):
        return self.nombre


class ProductoCotizado(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='productos_cotizados')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} unidades - Cotización #{self.cotizacion.id}'
