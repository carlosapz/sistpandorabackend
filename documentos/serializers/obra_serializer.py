from rest_framework import serializers
from documentos.models import Obra

class ObraSerializer(serializers.ModelSerializer):
    desviacion_presupuesto = serializers.SerializerMethodField()
    duracion_dias = serializers.SerializerMethodField()

    class Meta:
        model = Obra
        fields = [
            'id',
            'nombre',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'progreso',
            'presupuesto_estimado',
            'presupuesto_real',
            'estado',
            'desviacion_presupuesto',
            'duracion_dias',
        ]

    def get_desviacion_presupuesto(self, obj):
        return obj.calcular_desviacion_presupuesto()

    def get_duracion_dias(self, obj):
        return obj.calcular_duracion_dias()
