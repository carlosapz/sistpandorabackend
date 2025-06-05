from rest_framework import serializers
from documentos.models import Proyecto
from documentos.serializers.categoria_serializer import CategoriaSerializer


class ProyectoSerializer(serializers.ModelSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True)

    class Meta:
        model = Proyecto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'responsable',
            'categorias'
        ]
