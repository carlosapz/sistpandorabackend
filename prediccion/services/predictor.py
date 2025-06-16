import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import RobustScaler
from prediccion.utils.currency_utils import obtener_precio_dolar, obtener_dolar_paralelo
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# FACTOR GLOBAL PARA AJUSTE DE PARALELO (solo se aplica si NO se pasa tipo_cambio_valor)
AJUSTE_PARALELO_FACTOR = 0.75

def predecir_precio_actual(producto, tipo_cambio_origen="Oficial", tipo_cambio_valor=None, usar_cache=True, ajuste_suavizado=1.0, regular_variacion=True):
    """
    Predice el precio actual de un producto usando LSTM con regulación y suavizado.
    - tipo_cambio_valor: valor específico del dólar (predicho o simulado).
    - ajuste_suavizado: entre 0.0 y 1.0 (mezcla entre tipo_cambio_actual y tipo_cambio_valor).
    - regular_variacion: si True, aplica límites inferior/superior para evitar predicciones irreales.
    """
    cache_key = f"prediccion_precio_{producto.id}_{tipo_cambio_origen}_{tipo_cambio_valor or 'auto'}_{ajuste_suavizado}_{regular_variacion}"
    if usar_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            logger.info(f"✅ [CACHE] Precio predicho para producto {producto.id}: {cached} BOB")
            return cached

    if not producto.csv_datos or not producto.modelo_lstm:
        raise ValueError("El producto no tiene CSV ni modelo LSTM asociado.")

    try:
        df = pd.read_csv(producto.csv_datos.path)
    except Exception as e:
        logger.error(f"Error al leer CSV del producto: {e}")
        raise

    required_columns = [
        "fecha",
        "precio_unitario_usd",
        "precio_unitario_bob",
        "usd_bob_oficial",
        "usd_bob_paralelo"
    ]
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Faltan columnas requeridas en CSV")

    df = df.sort_values("fecha")
    df["tipo_cambio_oficial"] = df["usd_bob_oficial"]

    X = df[["precio_unitario_usd", "tipo_cambio_oficial", "usd_bob_paralelo"]].values
    y = df["precio_unitario_usd"].values

    scaler_X = RobustScaler()
    scaler_y = RobustScaler()

    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

    secuencia = X_scaled[-10:]
    modelo = load_model(producto.modelo_lstm.path, compile=False)
    pred_scaled = modelo.predict(secuencia.reshape(1, 10, 3))
    pred_usd = scaler_y.inverse_transform(pred_scaled)[0][0]

    # Tipo de cambio
    tipo_cambio_cache_key = f"tipo_cambio_{tipo_cambio_origen}"
    tipo_cambio_actual = cache.get(tipo_cambio_cache_key)
    if tipo_cambio_actual is None:
        tipo_cambio_actual = obtener_dolar_paralelo() if tipo_cambio_origen.lower() == "paralelo" else obtener_precio_dolar()
        cache.set(tipo_cambio_cache_key, tipo_cambio_actual, timeout=3600)

    if tipo_cambio_actual is None:
        raise ValueError("No se pudo obtener tipo de cambio actual")

    # Mezcla entre actual y valor predicho
    if tipo_cambio_valor is not None:
        tipo_cambio_final = (
            tipo_cambio_actual * (1 - ajuste_suavizado) + tipo_cambio_valor * ajuste_suavizado
        )
        logger.info(f"🧪 TC suavizado: actual={tipo_cambio_actual}, futuro={tipo_cambio_valor}, ajuste={ajuste_suavizado} → usado={tipo_cambio_final}")
    elif tipo_cambio_origen.lower() == "paralelo":
        tipo_cambio_final = tipo_cambio_actual * AJUSTE_PARALELO_FACTOR
        logger.info(f"🔄 Ajuste paralelo aplicado: {tipo_cambio_actual} * {AJUSTE_PARALELO_FACTOR} = {tipo_cambio_final}")
    else:
        tipo_cambio_final = tipo_cambio_actual

    precio_estimado_bob = float(pred_usd * tipo_cambio_final)

    if regular_variacion:
        precio_base = df["precio_unitario_bob"].iloc[-1]
        limite_inf = precio_base * 0.9
        limite_sup = precio_base * 1.5
        precio_final = min(max(precio_estimado_bob, limite_inf), limite_sup)
        precio_final = round(precio_final, 2)
        logger.info(f"✅ Precio regulado: {precio_final} BOB (Base: {precio_base} BOB)")
    else:
        precio_final = round(precio_estimado_bob, 2)
        logger.info(f"⚡ Precio sin regulación aplicado: {precio_final} BOB")

    if usar_cache:
        cache.set(cache_key, precio_final, timeout=600)

    return precio_final
