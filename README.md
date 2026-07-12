# Quant4all · Historical Index Constituents

Aplicación en Streamlit para consultar los **constituyentes históricos del S&P 500 y del Nasdaq 100** en cualquier momento desde el **1 de enero de 1990**.

![Quant4all](Logo.png)

## Funcionalidades

1. **Consulta por ticker** — selecciona (o escribe) un ticker vivo y verás su histórico de precios de Yahoo Finance con las fechas de **entrada y salida** del S&P 500 y del Nasdaq 100 marcadas sobre el gráfico. Las empresas deslistadas no se consultan en Yahoo (evita errores), pero sí se muestra su histórico en los índices.
2. **Constituyentes en una fecha** — elige un índice y una fecha; la app muestra cuántos constituyentes tenía y la tabla `Ticker · Empresa · Fecha de incorporación`, ordenada alfabéticamente y descargable a Excel.
3. **Entradas y salidas en un periodo** — elige un índice y un rango de fechas; lista primero las entradas y luego las salidas (cada bloque ordenado alfabéticamente), descargable a Excel.

Interfaz **bilingüe** (español / inglés).

## Datos

`Historical_Index_Constituent.xlsx` con tres pestañas:

- **SPX / NDX** — formato largo por eventos: `Ticker | Name | Date/Time | InSPX (o InNDX)`. Cada fila es una fecha de cambio de estado; el estado en una fecha es el flag de la última fila con fecha ≤ esa fecha. `0→1` = entrada, `1→0` = salida. Un `1` en 1990-01-02 significa "incorporada antes de 1990". Los tickers deslistados llevan el sufijo `-Delisted` (el mismo símbolo lo han usado empresas distintas a lo largo del tiempo).
- **Delisting Date** — fecha en la que cada ticker deslistado dejó de cotizar.

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio de GitHub.
2. En [share.streamlit.io](https://share.streamlit.io) crea una nueva app apuntando a `app.py`.
3. Asegúrate de que `Historical_Index_Constituent.xlsx` y `Logo.png` están incluidos en el repo.

> Los datos de índices son propios; los precios provienen de Yahoo Finance. No es asesoramiento financiero.
