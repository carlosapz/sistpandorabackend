from rest_framework import serializers
from prediccion.models.cotizacion import ProductoCotizado
from prediccion.models.producto import Producto
from .producto_serializer import ProductoSerializer

class ProductoCotizadoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )

    class Meta:
        model = ProductoCotizado
        fields = ['id', 'producto', 'producto_id', 'cantidad', 'precio_unitario', 'total']
