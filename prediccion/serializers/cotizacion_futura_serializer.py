from rest_framework import serializers
from prediccion.models.cotizacion_futura import CotizacionFutura

class CotizacionFuturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CotizacionFutura
        fields = "__all__"
