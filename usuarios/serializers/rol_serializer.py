from rest_framework import serializers
from usuarios.models.rol import Rol

class RolSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Rol.
    """
    class Meta:
        model = Rol
        fields = ['id', 'nombre']
