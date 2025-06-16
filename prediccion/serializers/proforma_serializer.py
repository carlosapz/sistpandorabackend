# prediccion/serializers/proforma_serializer.py
from rest_framework import serializers
from prediccion.models.proforma import Proforma
from prediccion.serializers.producto_serializer import ProductoSerializer
from prediccion.serializers.item_adicional_serializer import ItemAdicionalSerializer

class ProformaSerializer(serializers.ModelSerializer):
    productos = ProductoSerializer(many=True)
    items_adicionales = ItemAdicionalSerializer(many=True)

    class Meta:
        model = Proforma
        fields = '__all__'
