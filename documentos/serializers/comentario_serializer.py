from rest_framework import serializers
from documentos.models import Comentario

class ComentarioSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = Comentario
        fields = ['id', 'documento', 'usuario', 'contenido', 'fecha']
        read_only_fields = ['fecha', 'usuario']
