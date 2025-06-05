from django.db import models

class Categoria(models.Model):
    """
    Categoría asociada a los documentos y proyectos.
    """
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
