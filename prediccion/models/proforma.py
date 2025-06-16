# prediccion/models/proforma.py
from django.db import models
from prediccion.models.producto import Producto
from prediccion.models.item_adicional import ItemAdicional

class Proforma(models.Model):
    cliente = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    productos = models.ManyToManyField(Producto)
    items_adicionales = models.ManyToManyField(ItemAdicional)
    total_estimado = models.DecimalField(max_digits=15, decimal_places=2)

    def calcular_total(self):
        total = sum([producto.precio_unitario * producto.cantidad for producto in self.productos.all()])
        return total

    def __str__(self):
        return f"Proforma para {self.cliente} - Fecha: {self.fecha}"
