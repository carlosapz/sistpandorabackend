from rest_framework import serializers # type: ignore
from prediccion.models.prediccion_historica import PrediccionHistorica

class PrediccionHistoricaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    tipo_cambio_origen = serializers.CharField()
    tipo_cambio_utilizado = serializers.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        model = PrediccionHistorica
        fields = [
            "fecha_prediccion",
            "precio_estimado_bs",
            "precio_estimado_usd",
            "tipo_cambio_utilizado",
            "tipo_cambio_origen",
            "producto_nombre"
        ]
