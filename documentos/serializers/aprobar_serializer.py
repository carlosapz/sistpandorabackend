from rest_framework import serializers
from documentos.models import Documento

class DocumentoAprobarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = ['estado']
