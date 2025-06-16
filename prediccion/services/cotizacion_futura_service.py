from prediccion.models.cotizacion_futura import CotizacionFutura
from prediccion.models.cotizacion import Cotizacion, ProductoCotizado
from django.utils import timezone
from prediccion.services.predictor import predecir_precio_actual

def simular_cotizacion_futura(cotizacion: Cotizacion, dolar_futuro: float, horizonte_dias: int, user=None) -> CotizacionFutura:
    """
    Genera una simulación futura de la cotización usando el dolar_futuro proporcionado.
    """
    productos_simulados = []
    total_bs = 0.0

    productos_cotizados = ProductoCotizado.objects.filter(cotizacion=cotizacion)

    for prod in productos_cotizados:
        precio_estimado_bs = predecir_precio_actual(
            producto=prod.producto,
            tipo_cambio_origen="Paralelo",
            tipo_cambio_valor=dolar_futuro,
            usar_cache=False,
            ajuste_suavizado=0.5,
            regular_variacion=False  # Apagamos regulación sólo para simulación futura
        )

        if precio_estimado_bs is None:
            raise ValueError(f"No se pudo predecir precio para producto '{prod.producto.nombre}' (ID {prod.producto.id})")

        subtotal = precio_estimado_bs * prod.cantidad
        total_bs += subtotal

        productos_simulados.append({
            "producto_id": prod.producto.id,
            "nombre": prod.producto.nombre,
            "unidad_medida": prod.producto.unidad_medida,
            "precio_unitario": round(precio_estimado_bs, 2),
            "cantidad": prod.cantidad,
            "subtotal": round(subtotal, 2)
        })

    simulacion = CotizacionFutura.objects.create(
        cotizacion_original=cotizacion,
        nombre=f"Simulación a futuro ({timezone.now().date()})",
        dolar_usado=dolar_futuro,
        total_bs=round(total_bs, 2),
        productos_simulados=productos_simulados,
        proyecto_nombre=cotizacion.proyecto.nombre if cotizacion.proyecto else "-",
        categoria_nombre=cotizacion.categoria.nombre if cotizacion.categoria else "-",
        tipo_cambio_origen="Paralelo",
        horizonte_dias=horizonte_dias
    )

    return simulacion
