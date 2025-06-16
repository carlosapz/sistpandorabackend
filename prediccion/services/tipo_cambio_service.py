import datetime
from prediccion.models import TipoCambioHistorico, PrediccionTipoCambio, RegistroDolarSistema
from prediccion.utils.currency_utils import obtener_precio_dolar, obtener_dolar_paralelo


def guardar_tipo_cambio_historico():
    hoy = datetime.date.today()

    if TipoCambioHistorico.objects.filter(fecha=hoy).exists():
        return f"Ya existe registro para hoy ({hoy})."

    oficial = obtener_precio_dolar()
    paralelo = obtener_dolar_paralelo()

    TipoCambioHistorico.objects.create(
        fecha=hoy,
        tipo_cambio_oficial=oficial,
        tipo_cambio_paralelo=paralelo,
        fuente="api"
    )

    # Guardar también en RegistroDolarSistema para Prophet
    RegistroDolarSistema.objects.update_or_create(
        fecha=hoy,
        tipo_cambio_origen="Paralelo",
        defaults={
            "valor": paralelo,
            "fuente": "API"
        }
    )

    return f"Registro guardado para {hoy}: Oficial {oficial} - Paralelo {paralelo}."


def guardar_prediccion_tipo_cambio(horizonte_dias, tipo_cambio_origen, prediccion_dict, comentario=""):
    PrediccionTipoCambio.objects.create(
        horizonte_dias=horizonte_dias,
        tipo_cambio_origen=tipo_cambio_origen,
        prediccion_json=prediccion_dict,
        comentario=comentario
    )
    return "Predicción guardada."
