from django.db import models
from django.contrib.auth import get_user_model

from .categoria import Categoria

User = get_user_model()

class Proyecto(models.Model):
    """
    Representa un proyecto dentro de la empresa constructora.
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    activo = models.BooleanField(default=True)
    categorias = models.ManyToManyField(Categoria, related_name='proyectos', blank=True)

    class Meta:
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.nombre
