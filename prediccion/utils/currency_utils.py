# prediccion/utils/currency_utils.py
import requests
from bs4 import BeautifulSoup
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# API CONFIG
API_KEY = "b27b5ba2b351fa68f644543e"
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

def obtener_precio_dolar():
    """
    Obtiene el precio oficial del dólar en BOB. Cache 10 mins.
    """
    precio = cache.get('precio_dolar_oficial')
    if precio is not None:
        logger.info(f"✅ [CACHE] Precio oficial del dólar: {precio} BOB")
        return precio

    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        precio = data.get("conversion_rates", {}).get("BOB")
        if precio is None:
            raise ValueError("No se encontró la tasa de conversión BOB.")

        cache.set('precio_dolar_oficial', precio, timeout=600)  # 10 mins
        logger.info(f"✅ Precio oficial del dólar obtenido: {precio} BOB")
        return precio

    except Exception as e:
        logger.error(f"❌ Error al obtener precio oficial del dólar: {e}")
        return None

def obtener_dolar_paralelo():
    """
    Obtiene el dólar paralelo. Cache 10 mins.
    """
    precio = cache.get('precio_dolar_paralelo')
    if precio is not None:
        logger.info(f"✅ [CACHE] Dólar paralelo: {precio} BOB")
        return precio

    try:
        response = requests.get("https://dolarboliviahoy.com/api/getBuyPrice", timeout=5)
        response.raise_for_status()
        data = response.json()

        precio = data.get("averagePrice")
        if precio is None:
            raise ValueError("No se encontró averagePrice en la respuesta.")

        cache.set('precio_dolar_paralelo', precio, timeout=600)  # 10 mins
        logger.info(f"✅ Dólar paralelo obtenido: {precio} BOB")
        return precio

    except Exception as e:
        logger.error(f"⚠️ Error al obtener el dólar paralelo: {e}")
        return None
