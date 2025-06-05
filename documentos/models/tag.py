from django.db import models

class Tag(models.Model):
    """
    Etiqueta para categorizar documentos.
    """
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
