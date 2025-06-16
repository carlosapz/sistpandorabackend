from rest_framework import serializers
from prediccion.models.item_adicional import ItemAdicional

class ItemAdicionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemAdicional
        fields = ['id', 'descripcion', 'unidad', 'cantidad', 'precio_unitario', 'total']
