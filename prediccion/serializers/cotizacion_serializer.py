from rest_framework import serializers
from prediccion.models.cotizacion import Cotizacion, ProductoCotizado
from prediccion.models.item_adicional import ItemAdicional
from prediccion.serializers.producto_cotizado_serializer import ProductoCotizadoSerializer
from prediccion.serializers.item_adicional_serializer import ItemAdicionalSerializer
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class CotizacionSerializer(serializers.ModelSerializer):
    productos_cotizados = ProductoCotizadoSerializer(many=True)
    items_adicionales = ItemAdicionalSerializer(many=True)

    usuario = serializers.ReadOnlyField(source='usuario.username')
    proyecto_id = serializers.IntegerField(write_only=True, required=False)
    categoria_id = serializers.IntegerField(write_only=True, required=False)
    obra_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    proyecto_nombre = serializers.SerializerMethodField()
    categoria_nombre = serializers.SerializerMethodField()
    obra_nombre = serializers.SerializerMethodField()

    es_valida = serializers.SerializerMethodField()
    variacion_tipo_cambio = serializers.SerializerMethodField()

    tipo_cambio_origen = serializers.CharField(required=False)
    tipo_cambio_valor = serializers.DecimalField(max_digits=10, decimal_places=4, required=False)

    class Meta:
        model = Cotizacion
        fields = [
            'id',
            'usuario',
            'fecha',
            'nombre',
            'productos_cotizados',
            'items_adicionales',
            'proyecto_id',
            'categoria_id',
            'obra_id',
            'proyecto_nombre',
            'categoria_nombre',
            'obra_nombre',
            'fecha_validez',
            'tipo_cambio_origen',
            'tipo_cambio_valor',
            'variacion_tipo_cambio',
            'es_valida',
            'gastos_generales',
            'utilidad',
            'contingencia',
            'total_general',
        ]

    def get_proyecto_nombre(self, obj):
        return obj.proyecto.nombre if obj.proyecto else ""

    def get_categoria_nombre(self, obj):
        return obj.categoria.nombre if obj.categoria else ""

    def get_obra_nombre(self, obj):
        return obj.obra.nombre if obj.obra else ""

    def get_es_valida(self, obj):
        return obj.es_valida()

    def get_variacion_tipo_cambio(self, obj):
        if obj.tipo_cambio_valor is None or obj.tipo_cambio_dolar is None:
            return None
        variacion = Decimal(obj.tipo_cambio_valor) - Decimal(obj.tipo_cambio_dolar)
        return round(variacion, 4)

    def create(self, validated_data):
        productos_data = validated_data.pop('productos_cotizados', [])
        items_adicionales_data = validated_data.pop('items_adicionales', [])
        proyecto_id = validated_data.pop('proyecto_id', None)
        categoria_id = validated_data.pop('categoria_id', None)
        obra_id = validated_data.pop('obra_id', None)
        usuario = self.context['request'].user

        if not productos_data and not items_adicionales_data:
            raise serializers.ValidationError("La cotización debe incluir al menos un producto o ítem adicional.")

        if validated_data.get("tipo_cambio_valor") is None:
            raise serializers.ValidationError("Debe especificarse el tipo de cambio usado.")

        cotizacion = Cotizacion.objects.create(
            usuario=usuario,
            proyecto_id=proyecto_id,
            categoria_id=categoria_id,
            obra_id=obra_id,
            **validated_data
        )

        subtotal = Decimal("0.00")

        for producto in productos_data:
            if producto['cantidad'] <= 0 or producto['precio_unitario'] < 0:
                raise serializers.ValidationError("Cantidad o precio inválido en un producto cotizado.")
            total = producto['precio_unitario'] * producto['cantidad']
            ProductoCotizado.objects.create(
                cotizacion=cotizacion,
                producto=producto['producto'],
                cantidad=producto['cantidad'],
                precio_unitario=producto['precio_unitario'],
                total=total
            )
            subtotal += total

        for item in items_adicionales_data:
            if item['cantidad'] <= 0 or item['precio_unitario'] < 0:
                raise serializers.ValidationError("Cantidad o precio inválido en un ítem adicional.")
            total = item['precio_unitario'] * item['cantidad']
            ItemAdicional.objects.create(
                cotizacion=cotizacion,
                descripcion=item['descripcion'],
                unidad=item['unidad'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario'],
                total=total
            )
            subtotal += total

        gastos = subtotal * cotizacion.gastos_generales / 100
        utilidad = subtotal * cotizacion.utilidad / 100
        contingencia = subtotal * cotizacion.contingencia / 100

        total_general = subtotal + gastos + utilidad + contingencia
        cotizacion.total_general = total_general
        cotizacion.save()

        logger.info(f"✅ Cotización creada con total final: {total_general} BOB")
        return cotizacion

    def update(self, instance, validated_data):
        productos_data = validated_data.pop('productos_cotizados', [])
        items_adicionales_data = validated_data.pop('items_adicionales', [])
        obra_id = self.initial_data.get("obra_id", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if obra_id is not None:
            instance.obra_id = obra_id
        instance.save()

        instance.productos_cotizados.all().delete()
        instance.items_adicionales.all().delete()

        if not productos_data and not items_adicionales_data:
            raise serializers.ValidationError("La cotización debe incluir al menos un producto o ítem adicional.")

        if validated_data.get("tipo_cambio_valor") is None and instance.tipo_cambio_valor is None:
            raise serializers.ValidationError("Debe especificarse el tipo de cambio usado.")

        subtotal = Decimal("0.00")

        for producto in productos_data:
            if producto['cantidad'] <= 0 or producto['precio_unitario'] < 0:
                raise serializers.ValidationError("Cantidad o precio inválido en un producto cotizado.")
            total = producto['precio_unitario'] * producto['cantidad']
            ProductoCotizado.objects.create(
                cotizacion=instance,
                producto=producto['producto'],
                cantidad=producto['cantidad'],
                precio_unitario=producto['precio_unitario'],
                total=total
            )
            subtotal += total

        for item in items_adicionales_data:
            if item['cantidad'] <= 0 or item['precio_unitario'] < 0:
                raise serializers.ValidationError("Cantidad o precio inválido en un ítem adicional.")
            total = item['precio_unitario'] * item['cantidad']
            ItemAdicional.objects.create(
                cotizacion=instance,
                descripcion=item['descripcion'],
                unidad=item['unidad'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario'],
                total=total
            )
            subtotal += total

        gastos = subtotal * instance.gastos_generales / 100
        utilidad = subtotal * instance.utilidad / 100
        contingencia = subtotal * instance.contingencia / 100

        total_general = subtotal + gastos + utilidad + contingencia
        instance.total_general = total_general
        instance.save()

        logger.info(f"✅ Cotización actualizada con total final: {total_general} BOB")
        return instance
