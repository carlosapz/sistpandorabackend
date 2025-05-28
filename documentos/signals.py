from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Documento, HistorialActividad

@receiver(post_save, sender=Documento)
def log_documento_creation_or_update(sender, instance, created, **kwargs):
    if not instance.usuario:
        return

    accion = 'CREACION' if created else 'EDICION'

    if instance.pk:
        HistorialActividad.objects.create(
            usuario=instance.usuario,
            documento=instance,
            accion=accion
        )

@receiver(post_delete, sender=Documento)
def log_documento_deletion(sender, instance, **kwargs):
    if not instance.usuario:
        return

    HistorialActividad.objects.create(
        usuario=instance.usuario,
        accion="ELIMINACION"
    )
