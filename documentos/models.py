# documentos/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificaciones")
    mensaje = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje[:20]}"

class Proyecto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    activo = models.BooleanField(default=True)

    categorias = models.ManyToManyField('Categoria', related_name='proyectos', blank=True)

    class Meta:
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Tag(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Documento(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('PLANO', 'Plano'),
        ('CONTRATO', 'Contrato'),
        ('PERMISO', 'Permiso'),
        ('RENDER', 'Render'),
        ('ACUERDO', 'Acuerdo'),
        ('ESPECIFICACION', 'Especificación Técnica'),
        ('MEMORIA', 'Memoria de Cálculo'),
        ('INFORME', 'Informe Técnico'),
        ('OTRO', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('REVISION', 'En Revisión'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    PRIORIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=50, choices=TIPO_DOCUMENTO_CHOICES, default='OTRO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    archivo = models.FileField(upload_to='documentos/')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documentos_creados')
    usuario_modificacion = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos_modificados')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='REVISION', db_index=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None

        if es_nuevo and self.proyecto and Documento.objects.filter(titulo=self.titulo, proyecto=self.proyecto).exists():
            base = f"{self.titulo} ({self.proyecto.nombre})"
            nuevo_titulo = base
            contador = 1
            while Documento.objects.filter(titulo=nuevo_titulo).exists():
                nuevo_titulo = f"{base} ({contador})"
                contador += 1
            self.titulo = nuevo_titulo

        estado_anterior = None if es_nuevo else Documento.objects.get(pk=self.pk).estado

        super().save(*args, **kwargs)

        if es_nuevo and self.estado == 'REVISION':
            Notificacion.objects.create(
                usuario=self.usuario,
                mensaje=f"El documento '{self.titulo}' ha sido creado y está en revisión."
            )
        elif not es_nuevo:
            if estado_anterior != self.estado:
                if self.estado == 'APROBADO':
                    Notificacion.objects.create(
                        usuario=self.usuario,
                        mensaje=f"El documento '{self.titulo}' ha sido aprobado."
                    )
                elif self.estado == 'RECHAZADO':
                    Notificacion.objects.create(
                        usuario=self.usuario,
                        mensaje=f"El documento '{self.titulo}' ha sido rechazado."
                    )

    def __str__(self):
        return f"{self.titulo} ({self.estado})"

class VersionDocumento(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='versiones')
    archivo = models.FileField(upload_to='documentos/versiones/')
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Versión de {self.documento.titulo} - {self.fecha}"

class Comentario(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario por {self.usuario} en {self.documento}"


class HistorialActividad(models.Model):
    ACCIONES = [
        ('CREACION', 'Creación'),
        ('EDICION', 'Edición'),
        ('ELIMINACION', 'Eliminación'),
        ('APROBACION', 'Aprobación'),
        ('RECHAZO', 'Rechazo'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actividades')
    documento = models.ForeignKey('Documento', on_delete=models.SET_NULL, null=True, blank=True)

    accion = models.CharField(max_length=20, choices=ACCIONES)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accion} por {self.usuario} en {self.fecha}"

class ReporteHistorial(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    filtros_aplicados = models.TextField()
    tipo_reporte = models.CharField(max_length=10, default="PDF")

    def __str__(self):
        return f"Reporte generado por {self.usuario} el {self.fecha_generacion}"

class Obra(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    progreso = models.FloatField(default=0.0)
    presupuesto_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    presupuesto_real = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('EN_PROGRESO', 'En Progreso'),
        ('FINALIZADO', 'Finalizado'),
        ('PAUSADO', 'Pausado'),
        ('CANCELADO', 'Cancelado')
    ], default='EN_PROGRESO')

    def __str__(self):
        return f"{self.nombre} - {self.estado}"

    def calcular_desviacion_presupuesto(self):
        if self.presupuesto_real:
            return self.presupuesto_real - self.presupuesto_estimado
        return None
