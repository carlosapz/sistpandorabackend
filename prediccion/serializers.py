from rest_framework import serializers
from .models import Producto, Cotizacion, ProductoCotizado, PrediccionHistorica
from documentos.models import Proyecto, Categoria
from datetime import timedelta
from django.utils import timezone

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ProductoCotizadoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )

    class Meta:
        model = ProductoCotizado
        fields = ['id', 'producto', 'producto_id', 'cantidad', 'precio_unitario', 'total']

class CotizacionSerializer(serializers.ModelSerializer):
    productos_cotizados = ProductoCotizadoSerializer(many=True)
    usuario = serializers.ReadOnlyField(source='usuario.username')
    proyecto_id = serializers.IntegerField(write_only=True, required=False)
    categoria_id = serializers.IntegerField(write_only=True, required=False)
    proyecto_nombre = serializers.SerializerMethodField()
    categoria_nombre = serializers.SerializerMethodField()
    es_valida = serializers.SerializerMethodField()

    # Tipo de cambio campos
    tipo_cambio_origen = serializers.CharField(required=False)
    tipo_cambio_valor = serializers.DecimalField(max_digits=10, decimal_places=4, required=False)

    class Meta:
        model = Cotizacion
        fields = [
            'id', 'usuario', 'fecha', 'nombre', 'total_general',
            'productos_cotizados', 'proyecto_id', 'categoria_id',
            'proyecto_nombre', 'categoria_nombre', 'fecha_validez',
            'tipo_cambio_origen', 'tipo_cambio_valor',
            'es_valida',
        ]

    def get_proyecto_nombre(self, obj):
        return obj.proyecto.nombre if obj.proyecto else ""

    def get_categoria_nombre(self, obj):
        return obj.categoria.nombre if obj.categoria else ""

    def get_es_valida(self, obj):
        return obj.es_valida()

    def create(self, validated_data):
        productos_data = validated_data.pop('productos_cotizados')
        proyecto_id = validated_data.pop('proyecto_id', None)
        categoria_id = validated_data.pop('categoria_id', None)
        usuario = self.context['request'].user

        cotizacion = Cotizacion.objects.create(
            usuario=usuario,
            proyecto_id=proyecto_id,
            categoria_id=categoria_id,
            **validated_data
        )

        for producto_data in productos_data:
            ProductoCotizado.objects.create(
                cotizacion=cotizacion,
                producto=producto_data['producto'],
                cantidad=producto_data['cantidad'],
                precio_unitario=producto_data['precio_unitario'],
                total=producto_data['precio_unitario'] * producto_data['cantidad'],
            )

        return cotizacion

    def update(self, instance, validated_data):
        productos_data = validated_data.pop('productos_cotizados', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        instance.productos_cotizados.all().delete()

        for producto_data in productos_data:
            ProductoCotizado.objects.create(
                cotizacion=instance,
                producto=producto_data['producto'],
                cantidad=producto_data['cantidad'],
                precio_unitario=producto_data['precio_unitario'],
                total=producto_data['precio_unitario'] * producto_data['cantidad'],
            )

        return instance

class PrediccionHistoricaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrediccionHistorica
        fields = ["fecha_prediccion", "precio_estimado_bs", "precio_estimado_usd", "tipo_cambio_utilizado"]
