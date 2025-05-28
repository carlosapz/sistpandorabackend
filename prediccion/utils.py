# prediccion/utils.py
import requests
from bs4 import BeautifulSoup

API_KEY = "b27b5ba2b351fa68f644543e"
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

def obtener_precio_dolar():
    try:
        response = requests.get(API_URL)
        data = response.json()
        return data["conversion_rates"]["BOB"]
    except Exception as e:
        print("❌ Error al obtener precio oficial del dólar:", e)
        return None

def obtener_dolar_paralelo():
    try:
        response = requests.get("https://dolarboliviahoy.com/api/getBuyPrice")
        data = response.json()
        return data.get("averagePrice")
    except Exception as e:
        print("⚠️ Error al obtener el dólar paralelo:", e)
        return None