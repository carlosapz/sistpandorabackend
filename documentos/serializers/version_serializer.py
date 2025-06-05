from rest_framework import serializers
from documentos.models import VersionDocumento

class VersionDocumentoSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = VersionDocumento
        fields = ['id', 'documento', 'archivo', 'fecha', 'usuario', 'activo']
        read_only_fields = ['fecha', 'usuario', 'activo']
