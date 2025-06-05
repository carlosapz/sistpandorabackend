from rest_framework import serializers # type: ignore
from prediccion.models.prediccion_historica import PrediccionHistorica

class PrediccionHistoricaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo PrediccionHistorica.
    """
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = PrediccionHistorica
        fields = [
            "fecha_prediccion",
            "precio_estimado_bs",
            "precio_estimado_usd",
            "tipo_cambio_utilizado",
            "producto_nombre"
        ]
