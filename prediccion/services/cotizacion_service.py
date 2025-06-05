from decimal import Decimal
from typing import Optional
from prediccion.utils.currency_utils import obtener_precio_dolar, obtener_dolar_paralelo

def es_valida_cotizacion(tipo_cambio_origen: str, tipo_cambio_guardado: Optional[Decimal]) -> bool:
    """
    Calcula si la cotización es válida basado en el tipo de cambio actual
    y el tipo de cambio guardado, permitiendo un margen del 5%.

    Args:
        tipo_cambio_origen (str): "Oficial" o "Paralelo".
        tipo_cambio_guardado (Decimal): Valor guardado en la cotización.

    Returns:
        bool: True si la diferencia está dentro del margen permitido.
    """
    if tipo_cambio_guardado is None:
        return False

    tipo_cambio_actual = (
        obtener_dolar_paralelo() if tipo_cambio_origen == "Paralelo" else obtener_precio_dolar()
    )
    if tipo_cambio_actual is None:
        return False

    try:
        actual = Decimal(str(tipo_cambio_actual))
        guardado = Decimal(str(tipo_cambio_guardado))
        diferencia = abs(guardado - actual) / guardado
        return diferencia <= Decimal("0.05")
    except Exception:
        return False
