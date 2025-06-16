"""
Admin para el módulo de predicción: gestiona productos, cotizaciones y predicciones históricas.
"""
from django.contrib import admin
from .models.producto import Producto
from .models.cotizacion import Cotizacion, ProductoCotizado
from .models.prediccion_historica import PrediccionHistorica

from .models.tipo_cambio import ModeloTipoCambioConfig


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Admin de productos."""
    list_display = ('nombre', 'unidad_medida', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    """Admin de cotizaciones."""
    list_display = ('nombre', 'usuario', 'proyecto', 'categoria', 'total_general', 'fecha')
    list_filter = ('fecha', 'proyecto', 'categoria')
    search_fields = ('nombre', 'usuario__username', 'proyecto__nombre', 'categoria__nombre')
    readonly_fields = ('fecha', 'fecha_prediccion', 'fecha_validez')  # Evita edición manual de fechas

@admin.register(ProductoCotizado)
class ProductoCotizadoAdmin(admin.ModelAdmin):
    """Admin de productos cotizados."""
    list_display = ('cotizacion', 'producto', 'cantidad', 'precio_unitario', 'total')
    search_fields = ('producto__nombre',)

@admin.register(PrediccionHistorica)
class PrediccionHistoricaAdmin(admin.ModelAdmin):
    """Admin de predicciones históricas."""
    list_display = ('producto', 'precio_estimado_bs', 'precio_estimado_usd', 'fecha_prediccion', 'usuario')
    list_filter = ('fecha_prediccion', 'tipo_cambio_origen')
    search_fields = ('producto__nombre', 'usuario__username')
    readonly_fields = ('fecha_prediccion',)


@admin.register(ModeloTipoCambioConfig)
class ModeloTipoCambioConfigAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_cambio_origen', 'activo', 'fecha_subida')
    list_filter = ('tipo_cambio_origen', 'activo')
    search_fields = ('nombre',)
