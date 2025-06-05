from django.db import models

class Obra(models.Model):
    """
    Modelo que representa una obra en ejecución o finalizada.
    """
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    progreso = models.FloatField(default=0.0)
    presupuesto_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    presupuesto_real = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('EN_PROGRESO', 'En Progreso'),
            ('FINALIZADO', 'Finalizado'),
            ('PAUSADO', 'Pausado'),
            ('CANCELADO', 'Cancelado')
        ],
        default='EN_PROGRESO'
    )

    def __str__(self):
        return f"{self.nombre} - {self.estado}"

    def calcular_desviacion_presupuesto(self):
        """
        Calcula la diferencia entre el presupuesto real y estimado.
        """
        if self.presupuesto_real:
            return self.presupuesto_real - self.presupuesto_estimado
        return None
