from django.db import models
from usuarios.models import Usuario
from documentos.models import Proyecto, Categoria
from prediccion.models.producto import Producto
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from typing import Optional
from prediccion.services.cotizacion_service import es_valida_cotizacion

def obtener_fecha_validez() -> timezone.datetime:
    """
    Retorna la fecha de validez de la cotización: una semana desde el momento actual.
    """
    return timezone.now() + timedelta(weeks=1)

class Cotizacion(models.Model):
    """
    Modelo que representa una cotización realizada por un usuario para un proyecto.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cotizaciones')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='cotizaciones')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='cotizaciones', default=1)
    nombre = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    total_general = models.DecimalField(max_digits=15, decimal_places=2)
    fecha_prediccion = models.DateTimeField(auto_now=True)
    fecha_validez = models.DateTimeField(default=obtener_fecha_validez)
    tipo_cambio_dolar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    TIPO_CAMBIO_ORIGEN_CHOICES = [
        ("Oficial", "Oficial"),
        ("Paralelo", "Paralelo")
    ]
    tipo_cambio_origen = models.CharField(max_length=20, choices=TIPO_CAMBIO_ORIGEN_CHOICES, default="Oficial")
    tipo_cambio_valor = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    def es_valida(self) -> bool:
        """
        Verifica si la cotización es válida comparando el tipo de cambio guardado
        con el tipo de cambio actual, permitiendo un margen del 5%.
        """
        return es_valida_cotizacion(self.tipo_cambio_origen, self.tipo_cambio_dolar)

    def __str__(self):
        return self.nombre

class ProductoCotizado(models.Model):
    """
    Modelo que representa un producto incluido en una cotización.
    """
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='productos_cotizados')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} unidades - Cotización #{self.cotizacion.id}'
