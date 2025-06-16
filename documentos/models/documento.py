from django.db import models
from django.contrib.auth import get_user_model
from .proyecto import Proyecto
from .categoria import Categoria
from .tag import Tag
from .notificacion import Notificacion

User = get_user_model()

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
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, related_name='documentos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='documentos')
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
            Notificacion.objects.create(usuario=self.usuario, mensaje=f"El documento '{self.titulo}' ha sido creado y está en revisión.")
        elif not es_nuevo and estado_anterior != self.estado:
            Notificacion.objects.create(usuario=self.usuario, mensaje=f"El documento '{self.titulo}' ha sido {self.estado.lower()}.")

    def __str__(self):
        return f"{self.titulo} ({self.estado})"
