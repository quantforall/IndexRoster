"""Traducciones bilingües (ES / EN) para la interfaz."""

TRANSLATIONS = {
    # --- Generales / navegación ---
    "app_title": {"es": "Constituyentes Históricos de Índices", "en": "Historical Index Constituents"},
    "app_subtitle": {
        "es": "S&P 500 y Nasdaq 100 · desde el 1 de enero de 1990",
        "en": "S&P 500 & Nasdaq 100 · since January 1, 1990",
    },
    "db_updated": {
        "es": "📅 Base de datos actualizada hasta {date}",
        "en": "📅 Database updated through {date}",
    },
    "language": {"es": "Idioma", "en": "Language"},
    "choose_action": {"es": "¿Qué quieres hacer?", "en": "What do you want to do?"},
    "action_ticker": {"es": "🔎 Consultar un ticker", "en": "🔎 Look up a ticker"},
    "action_constituents": {
        "es": "📅 Constituyentes en una fecha",
        "en": "📅 Constituents on a date",
    },
    "action_changes": {
        "es": "🔁 Entradas y salidas en un periodo",
        "en": "🔁 Additions & removals in a period",
    },
    "choose_index": {"es": "Elige el índice", "en": "Choose the index"},
    "navigation": {"es": "Navegación", "en": "Navigation"},

    # --- Funcionalidad 1: ticker ---
    "f1_header": {"es": "Consulta por ticker", "en": "Ticker lookup"},
    "f1_intro": {
        "es": "Selecciona un ticker vivo o escribe uno. Verás su histórico de precios "
        "(Yahoo Finance) con las fechas de entrada y salida del S&P 500 y del Nasdaq 100.",
        "en": "Pick a live ticker or type one. You'll see its price history "
        "(Yahoo Finance) with S&P 500 and Nasdaq 100 add/remove dates marked.",
    },
    "f1_select": {"es": "Ticker (desplegable con buscador)", "en": "Ticker (searchable dropdown)"},
    "f1_free": {"es": "…o escribe un ticker libre", "en": "…or type a free ticker"},
    "f1_free_help": {
        "es": "Si escribes algo aquí, tiene prioridad sobre el desplegable.",
        "en": "If you type here, it overrides the dropdown.",
    },
    "f1_none": {"es": "— ninguno —", "en": "— none —"},
    "f1_run": {"es": "Consultar", "en": "Look up"},
    "f1_loading": {"es": "Descargando datos de Yahoo Finance…", "en": "Fetching data from Yahoo Finance…"},
    "f1_price": {"es": "Precio de cierre", "en": "Close price"},
    "f1_chart_title": {"es": "Cotización e histórico en índices", "en": "Price & index membership history"},
    "f1_no_price": {
        "es": "No se han podido obtener datos de precio de Yahoo Finance para este ticker. "
        "Aun así, abajo tienes su histórico de pertenencia a los índices.",
        "en": "Could not fetch price data from Yahoo Finance for this ticker. "
        "You still have its index membership history below.",
    },
    "f1_delisted_warning": {
        "es": "⚠️ Este ticker corresponde a una empresa deslistada. No se consulta Yahoo Finance "
        "(no habría datos), pero puedes ver su histórico en los índices.",
        "en": "⚠️ This ticker is a delisted company. Yahoo Finance is not queried "
        "(no data available), but you can still see its index history.",
    },
    "f1_membership": {"es": "Pertenencia a índices", "en": "Index membership"},
    "f1_never": {"es": "Nunca ha pertenecido a este índice.", "en": "Never a member of this index."},
    "f1_in_since_before": {"es": "En el índice desde **antes de 1990**", "en": "In the index since **before 1990**"},
    "f1_entered": {"es": "Entrada", "en": "Added"},
    "f1_exited": {"es": "Salida", "en": "Removed"},
    "f1_still_in": {"es": "sigue dentro", "en": "still a member"},
    "f1_before_1990": {"es": "antes de 1990", "en": "before 1990"},
    "f1_delist_date": {"es": "Fecha de deslistado (dejó de cotizar)", "en": "Delisting date (stopped trading)"},
    "f1_empty": {"es": "Introduce o selecciona un ticker para empezar.", "en": "Enter or select a ticker to start."},
    "f1_not_current": {
        "es": "ℹ️ Este ticker **no pertenece actualmente** ni al S&P 500 ni al Nasdaq 100.",
        "en": "ℹ️ This ticker is **not currently a member** of the S&P 500 or the Nasdaq 100.",
    },

    # --- Funcionalidad 2: constituyentes en una fecha ---
    "f2_header": {"es": "Constituyentes en una fecha", "en": "Constituents on a date"},
    "f2_date": {"es": "Fecha", "en": "Date"},
    "f2_count": {
        "es": "El **{index}** tenía **{n}** constituyentes el **{date}**.",
        "en": "The **{index}** had **{n}** constituents on **{date}**.",
    },
    "f2_table_cols": {
        "es": {
            "Ticker": "Ticker",
            "Name": "Empresa",
            "Entry": "Fecha de incorporación",
            "Delisting": "Fecha de deslistado",
        },
        "en": {
            "Ticker": "Ticker",
            "Name": "Company",
            "Entry": "Date added",
            "Delisting": "Delisting date",
        },
    },
    "f2_empty": {"es": "No hay constituyentes en esa fecha.", "en": "No constituents on that date."},

    # --- Funcionalidad 3: entradas y salidas en un periodo ---
    "f3_header": {"es": "Entradas y salidas en un periodo", "en": "Additions & removals in a period"},
    "f3_start": {"es": "Fecha de inicio", "en": "Start date"},
    "f3_end": {"es": "Fecha de fin", "en": "End date"},
    "f3_entries": {"es": "🟢 Entradas ({n})", "en": "🟢 Additions ({n})"},
    "f3_exits": {"es": "🔴 Salidas ({n})", "en": "🔴 Removals ({n})"},
    "f3_none_entries": {"es": "Sin entradas en este periodo.", "en": "No additions in this period."},
    "f3_none_exits": {"es": "Sin salidas en este periodo.", "en": "No removals in this period."},
    "f3_table_cols": {
        "es": {"Ticker": "Ticker", "Name": "Empresa", "Date": "Fecha", "Delisting": "Fecha de deslistado"},
        "en": {"Ticker": "Ticker", "Name": "Company", "Date": "Date", "Delisting": "Delisting date"},
    },
    "f3_bad_range": {"es": "La fecha de inicio debe ser anterior a la de fin.", "en": "Start date must be before end date."},

    # --- Descargas ---
    "download_xlsx": {"es": "⬇️ Descargar Excel", "en": "⬇️ Download Excel"},

    # --- Newsletter ---
    "newsletter_title": {"es": "📬 Únete a la newsletter de Quant4all", "en": "📬 Join the Quant4all newsletter"},
    "newsletter_text": {
        "es": "Trading sistemático | Acciones, ETFs y Futuros | Amibroker. Creando sistemas que "
        "sobreviven al trading real. Comparto lo que realmente funciona. Y tengo un curso gratuito: "
        "Trading Cuantitativo Desde Cero",
        "en": "Systematic trading | Stocks, ETFs & Futures | Amibroker. Building systems that "
        "survive real trading. I share what actually works. Plus a free course: "
        "Quantitative Trading From Scratch",
    },
    "newsletter_button": {"es": "Suscribirme gratis", "en": "Subscribe for free"},

    # --- Footer / varios ---
    "footer": {
        "es": "Datos de índices propios · precios vía Yahoo Finance · no es asesoramiento financiero.",
        "en": "Proprietary index data · prices via Yahoo Finance · not financial advice.",
    },
    "date_before_min": {
        "es": "La base de datos empieza el 1 de enero de 1990.",
        "en": "The database starts on January 1, 1990.",
    },
}


def make_translator(lang: str):
    def t(key: str):
        entry = TRANSLATIONS.get(key)
        if entry is None:
            return key
        return entry.get(lang, entry.get("es", key))

    return t
