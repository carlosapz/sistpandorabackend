from rest_framework import serializers
from documentos.models import HistorialActividad

class HistorialActividadSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source='usuario.username')
    documento = serializers.CharField(source='documento.titulo')

    class Meta:
        model = HistorialActividad
        fields = ['id', 'usuario', 'documento', 'accion', 'fecha']
