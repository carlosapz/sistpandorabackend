from rest_framework import serializers
from documentos.models import Obra

class ObraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obra
        fields = '__all__'
