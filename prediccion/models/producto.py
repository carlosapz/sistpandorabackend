from django.db import models

class Producto(models.Model):
    """
    Modelo que representa un producto con su información y datos asociados.
    """
    nombre: str = models.CharField(max_length=255)
    unidad_medida: str = models.CharField(max_length=50)
    descripcion: str = models.TextField(blank=True)
    modelo_lstm = models.FileField(upload_to='modelos_lstm/')
    csv_datos = models.FileField(upload_to='datasets_productos/')
    activo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.nombre
