from rest_framework import serializers
from usuarios.models.usuario import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario, incluye información básica y nombre del rol.
    """
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'is_active', 'is_staff', 'rol', 'rol_nombre'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        """
        Si se recibe 'password', la setea de forma segura.
        """
        if "password" in validated_data:
            instance.set_password(validated_data.pop("password"))
        return super().update(instance, validated_data)

    def create(self, validated_data):
        """
        Crea usuario asegurando el hash seguro de la contraseña.
        """
        password = validated_data.pop('password', None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
