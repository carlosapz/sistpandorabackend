# prediccion/services/predictor.py
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from prediccion.utils.currency_utils import obtener_precio_dolar, obtener_dolar_paralelo
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def predecir_precio_actual(producto, tipo_cambio_origen="Oficial", tipo_cambio_valor=None):
    """
    Predice el precio actual de un producto usando un modelo LSTM entrenado.
    Cache por producto/tipo de cambio por 10 min.
    """
    cache_key = f"prediccion_precio_{producto.id}_{tipo_cambio_origen}_{tipo_cambio_valor or 'auto'}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.info(f"✅ [CACHE] Precio predicho para producto {producto.id}: {cached_result} BOB")
        return cached_result

    if not producto.csv_datos or not producto.modelo_lstm:
        raise ValueError("El producto no tiene CSV ni modelo LSTM asociado.")

    df = pd.read_csv(producto.csv_datos.path)
    df = df.sort_values("fecha")

    if "tipo_cambio_oficial" not in df.columns:
        if "precio_unitario_bob" in df.columns and "precio_unitario_usd" in df.columns:
            df["tipo_cambio_oficial"] = df["precio_unitario_bob"] / df["precio_unitario_usd"]
        else:
            raise ValueError("El CSV no contiene las columnas necesarias para calcular tipo de cambio.")

    X_total = df[["precio_unitario_usd", "tipo_cambio_oficial"]].values
    y_total = df["precio_unitario_usd"].values

    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    X_norm = scaler_X.fit_transform(X_total)
    y_norm = scaler_y.fit_transform(y_total.reshape(-1, 1))

    secuencia = X_norm[-10:]

    modelo = load_model(producto.modelo_lstm.path, compile=False)

    pred_norm = modelo.predict(secuencia.reshape(1, 10, 2))
    pred_usd = scaler_y.inverse_transform(pred_norm)[0][0]

    if tipo_cambio_valor is None:
        if tipo_cambio_origen.lower() == "paralelo":
            tipo_cambio_actual = obtener_dolar_paralelo()
        else:
            tipo_cambio_actual = obtener_precio_dolar()
    else:
        tipo_cambio_actual = tipo_cambio_valor

    if tipo_cambio_actual is None:
        raise ValueError("No se pudo obtener el tipo de cambio actual.")

    precio_estimado_bob = round(float(pred_usd * tipo_cambio_actual), 2)

    # Guardar en cache por 10 min
    cache.set(cache_key, precio_estimado_bob, timeout=600)
    logger.info(f"✅ Precio predicho calculado para producto {producto.id}: {precio_estimado_bob} BOB")

    return precio_estimado_bob
