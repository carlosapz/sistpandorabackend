import pandas as pd
from prophet import Prophet
from prediccion.models import RegistroDolarSistema
from prediccion.utils.currency_utils import obtener_dolar_paralelo, obtener_precio_dolar
from datetime import datetime

def obtener_dataframe_actualizado():
    csv_path = "modelos_tipo_cambio/historico_dolarboliviahoy.csv"
    df_csv = pd.read_csv(csv_path)
    df_csv["fecha"] = pd.to_datetime(df_csv["fecha"])
    df_csv = df_csv[["fecha", "precio_compra"]].rename(columns={"precio_compra": "y"})

    registros = RegistroDolarSistema.objects.order_by("fecha").values("fecha", "valor")
    df_extra = pd.DataFrame(registros)
    if not df_extra.empty:
        df_extra["fecha"] = pd.to_datetime(df_extra["fecha"])
        df_extra = df_extra.rename(columns={"valor": "y"})

    df = pd.concat([df_csv, df_extra], ignore_index=True)
    df = df.sort_values("fecha").drop_duplicates("fecha", keep="last")
    df = df.rename(columns={"fecha": "ds"})

    return df


def generar_forecast_prophet(horizonte_dias=90, tipo_cambio_origen="Paralelo"):
    df = obtener_dataframe_actualizado()

    modelo = Prophet(
        daily_seasonality=True,
        yearly_seasonality=False,
        weekly_seasonality=True,
        changepoint_prior_scale=5.0
    )
    modelo.add_seasonality(name="mensual", period=30.5, fourier_order=5)
    modelo.add_seasonality(name="cuatrimestral", period=120.5, fourier_order=5)

    modelo.fit(df)
    future = modelo.make_future_dataframe(periods=horizonte_dias)
    forecast = modelo.predict(future)

    forecast_final = forecast[["ds", "yhat"]].tail(horizonte_dias)

    # Ajustar al valor real del dólar actual
    valor_modelo = df["y"].iloc[-1]
    valor_real = obtener_dolar_paralelo() if tipo_cambio_origen.lower() == "paralelo" else obtener_precio_dolar()
    factor_ajuste = valor_real / valor_modelo
    forecast_final["yhat"] *= factor_ajuste

    prediccion_json = [
        {"fecha": fila["ds"].strftime("%Y-%m-%d"), "valor": round(fila["yhat"], 4)}
        for _, fila in forecast_final.iterrows()
    ]

    return prediccion_json
