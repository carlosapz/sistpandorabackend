# documentos/serializers/HistorialActividadSerializer.py

from rest_framework import serializers
from documentos.models import HistorialActividad

class HistorialActividadSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()
    documento = serializers.SerializerMethodField()

    class Meta:
        model = HistorialActividad
        fields = ['id', 'usuario', 'documento', 'accion', 'fecha']

    def get_usuario(self, obj):
        return obj.usuario.username if obj.usuario else "Sistema"

    def get_documento(self, obj):
        return obj.documento.titulo if obj.documento else "Sin documento"
