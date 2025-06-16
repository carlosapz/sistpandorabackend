from django.db import models

class TipoCambioHistorico(models.Model):
    fecha = models.DateField(unique=True)
    tipo_cambio_oficial = models.FloatField(null=True, blank=True)
    tipo_cambio_paralelo = models.FloatField(null=True, blank=True)
    fuente = models.CharField(max_length=100, default='api')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fecha} - Oficial: {self.tipo_cambio_oficial} / Paralelo: {self.tipo_cambio_paralelo}"


class ModeloTipoCambioConfig(models.Model):
    nombre = models.CharField(max_length=100)
    modelo_file = models.FileField(upload_to='modelos_tipo_cambio/')
    csv_dataset_file = models.FileField(upload_to='datasets_tipo_cambio/')
    tipo_cambio_origen = models.CharField(max_length=20, choices=[('Oficial', 'Oficial'), ('Paralelo', 'Paralelo')])
    fecha_subida = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} ({self.tipo_cambio_origen}) - Activo: {self.activo}"


class PrediccionTipoCambio(models.Model):
    fecha_prediccion = models.DateField(auto_now_add=True)
    horizonte_dias = models.IntegerField()
    tipo_cambio_origen = models.CharField(max_length=20, choices=[('Oficial', 'Oficial'), ('Paralelo', 'Paralelo')])
    prediccion_json = models.JSONField()
    comentario = models.TextField(blank=True, null=True)
    nombre_modelo = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Predicción {self.tipo_cambio_origen} ({self.horizonte_dias} días) - {self.fecha_prediccion}"
