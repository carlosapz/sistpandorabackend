from rest_framework import serializers
from prediccion.models import PrediccionTipoCambio

class PrediccionTipoCambioSerializer(serializers.ModelSerializer):
    resumen = serializers.SerializerMethodField()

    class Meta:
        model = PrediccionTipoCambio
        fields = '__all__'

    def get_resumen(self, obj):
        pred = obj.prediccion_json
        if not pred or len(pred) < 2:
            return "Sin datos suficientes"
        
        valor_inicial = pred[0]["valor"]
        valor_final = pred[-1]["valor"]
        variacion = ((valor_final - valor_inicial) / valor_inicial) * 100
        tendencia = "Subida" if variacion > 0 else "Bajada"

        return {
            "valor_inicial": valor_inicial,
            "valor_final": valor_final,
            "variacion_pct": round(variacion, 2),
            "tendencia": tendencia
        }
