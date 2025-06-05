from rest_framework import serializers
from prediccion.models.producto import Producto

class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Producto.
    """
    class Meta:
        model = Producto
        fields = '__all__'
