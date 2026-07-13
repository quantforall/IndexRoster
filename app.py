"""
Quant4all · Constituyentes Históricos de Índices (S&P 500 y Nasdaq 100)

App Streamlit con tres funcionalidades:
  1. Consulta por ticker (gráfico de Yahoo Finance + entradas/salidas en ambos índices).
  2. Constituyentes del índice en una fecha concreta.
  3. Entradas y salidas del índice en un rango de fechas.
"""

from __future__ import annotations

import datetime as dt
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data as D
from i18n import make_translator

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "Logo.png"

# --- Paleta de marca Quant4all ---
NAVY_BG = "#0A1428"
NAVY_CARD = "#12203A"
ORANGE = "#F7931E"
BLUE = "#4EA8DE"
WHITE = "#FFFFFF"
MUTED = "#A9B4C4"

NEWSLETTER_URL = "https://quant4all.substack.com/"


def sub_url(source: str) -> str:
    """Enlace de suscripción con UTM para medir de dónde vienen los suscriptores."""
    return f"{NEWSLETTER_URL}?utm_source=app&utm_medium={source}&utm_campaign=index_roster"

# Fecha hasta la que están actualizados los datos. Al actualizar el Excel, cambia
# SOLO esta fecha: de aquí salen el límite del selector de fechas y el texto de la
# alerta (en ambos idiomas).
DATA_AS_OF = dt.date(2026, 7, 10)
DB_MIN = D.DB_START.date()
DB_MAX = DATA_AS_OF

_MONTHS_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
_MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def as_of_str(lang: str) -> str:
    """Fecha de actualización en formato largo según idioma."""
    d = DATA_AS_OF
    if lang == "es":
        return f"{d.day} de {_MONTHS_ES[d.month - 1]} de {d.year}"
    return f"{_MONTHS_EN[d.month - 1]} {d.day}, {d.year}"

st.set_page_config(
    page_title="Quant4all · Index Roster",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
def inject_css():
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {NAVY_BG}; }}
        section[data-testid="stSidebar"] {{ background-color: {NAVY_CARD}; }}
        h1, h2, h3, h4 {{ color: {WHITE}; letter-spacing: .2px; }}
        .q4a-hero-title {{
            font-size: 2.0rem; font-weight: 800; color: {WHITE};
            margin-bottom: .1rem; line-height: 1.15;
        }}
        .q4a-hero-title span {{ color: {ORANGE}; }}
        .q4a-hero-sub {{ color: {MUTED}; font-size: 1.0rem; margin-top: 0; }}
        .q4a-accent-rule {{
            height: 3px; border: none; border-radius: 3px; margin: .6rem 0 1.4rem 0;
            background: linear-gradient(90deg, {ORANGE} 0%, {ORANGE} 55%, rgba(247,147,30,0) 100%);
        }}
        .q4a-update {{
            display: inline-block; background: rgba(247,147,30,.12);
            border: 1px solid rgba(247,147,30,.55); border-left: 4px solid {ORANGE};
            color: {ORANGE}; font-weight: 700; padding: .55rem 1rem;
            border-radius: 8px; margin: .35rem 0 .2rem 0;
        }}
        .q4a-metric {{
            background: {NAVY_CARD}; border: 1px solid rgba(247,147,30,.25);
            border-left: 4px solid {ORANGE}; border-radius: 12px;
            padding: 1.1rem 1.3rem; margin: .3rem 0 1.1rem 0;
        }}
        .q4a-metric .val {{ font-size: 2.2rem; font-weight: 800; color: {ORANGE}; line-height: 1; }}
        .q4a-metric .lbl {{ color: {MUTED}; font-size: .95rem; margin-top: .35rem; }}
        .q4a-news {{
            background: linear-gradient(135deg, {NAVY_CARD} 0%, #17294a 100%);
            border: 1px solid rgba(247,147,30,.35); border-radius: 14px;
            padding: 1.2rem 1.4rem; margin: 1.2rem 0;
        }}
        .q4a-news h4 {{ margin: 0 0 .3rem 0; color: {WHITE}; }}
        .q4a-news p {{ color: {MUTED}; margin: 0 0 .8rem 0; }}
        .q4a-news a {{
            display: inline-block; background: {ORANGE}; color: {NAVY_BG} !important;
            font-weight: 700; text-decoration: none; padding: .55rem 1.2rem;
            border-radius: 8px; transition: transform .08s ease, filter .15s ease;
        }}
        .q4a-news a:hover {{ filter: brightness(1.08); transform: translateY(-1px); }}
        .q4a-cta {{
            display: flex; align-items: center; justify-content: space-between;
            gap: 1rem; flex-wrap: wrap;
            background: rgba(247,147,30,.10); border: 1px solid rgba(247,147,30,.4);
            border-radius: 12px; padding: 0 .8rem; min-height: 2.5rem; margin: 0;
        }}
        .q4a-cta .txt {{ color: {WHITE}; font-weight: 600; }}
        .q4a-cta a {{
            display: inline-block; background: {ORANGE}; color: {NAVY_BG} !important;
            font-weight: 700; text-decoration: none; padding: .3rem 1rem;
            border-radius: 8px; white-space: nowrap; transition: filter .15s ease;
        }}
        .q4a-cta a:hover {{ filter: brightness(1.08); }}
        .q4a-pill {{
            display:inline-block; padding:.15rem .6rem; border-radius:999px;
            font-size:.8rem; font-weight:700; margin-left:.4rem;
        }}
        .q4a-pill.in {{ background: rgba(78,168,222,.18); color:{BLUE}; border:1px solid {BLUE}; }}
        .q4a-pill.out {{ background: rgba(247,147,30,.15); color:{ORANGE}; border:1px solid {ORANGE}; }}
        .q4a-footer {{ color:{MUTED}; font-size:.85rem; text-align:center; margin-top:2rem;
            padding-top:1rem; border-top:1px solid rgba(169,180,196,.15); }}
        div[data-testid="stSegmentedControl"] [role="radiogroup"],
        div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] {{
            flex-wrap: nowrap !important; justify-content: flex-end;
        }}
        .stButton>button, .stDownloadButton>button {{
            background: {ORANGE}; color: {NAVY_BG}; font-weight: 700; border: none;
            border-radius: 8px;
        }}
        .stButton>button:hover, .stDownloadButton>button:hover {{ filter: brightness(1.08); color:{NAVY_BG}; }}

        /* ===== Robustez de tema: fuerza el look oscuro aunque Streamlit NO cargue
           el tema (p. ej. si config.toml no queda en la raíz del repo en Cloud) ===== */
        [data-testid="stHeader"] {{ background: transparent !important; }}
        .stApp, .stApp p, .stApp li, .stApp label, .stApp span,
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] *,
        [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
        [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] strong,
        [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {{
            color: {WHITE} !important;
        }}
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {{ color: {WHITE} !important; }}
        /* Reafirma los colores propios (que no queden blancos) */
        [data-testid="stMarkdownContainer"] .q4a-hero-sub,
        [data-testid="stMarkdownContainer"] .q4a-metric .lbl,
        [data-testid="stMarkdownContainer"] .q4a-news p,
        [data-testid="stMarkdownContainer"] .q4a-footer {{ color: {MUTED} !important; }}
        [data-testid="stMarkdownContainer"] .q4a-metric .val,
        [data-testid="stMarkdownContainer"] .q4a-update,
        [data-testid="stMarkdownContainer"] .q4a-pill.out {{ color: {ORANGE} !important; }}
        [data-testid="stMarkdownContainer"] .q4a-pill.in {{ color: {BLUE} !important; }}
        [data-testid="stMarkdownContainer"] .q4a-news a,
        [data-testid="stMarkdownContainer"] .q4a-cta a {{ color: {NAVY_BG} !important; }}
        /* Inputs (select, texto, fecha) oscuros con texto claro */
        [data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"] {{
            background-color: {NAVY_CARD} !important;
        }}
        [data-baseweb="select"] div, [data-baseweb="input"] input,
        [data-baseweb="base-input"] input {{ color: {WHITE} !important; }}
        [data-baseweb="input"] input::placeholder {{ color: {MUTED} !important; }}
        /* Desplegable de opciones oscuro */
        ul[role="listbox"], [data-baseweb="menu"], [data-baseweb="popover"] [role="listbox"] {{
            background-color: {NAVY_CARD} !important;
        }}
        li[role="option"], li[role="option"] * {{ color: {WHITE} !important; }}
        /* Acento naranja en radios y segmented control aunque no cargue el tema */
        [data-baseweb="radio"] [aria-checked="true"] div:first-child {{
            background-color: {ORANGE} !important; border-color: {ORANGE} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Carga de datos (cache)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_data():
    return D.load_all()


@st.cache_data(show_spinner=False)
def get_live_tickers():
    return D.live_tickers(get_data())


@st.cache_data(show_spinner=True, ttl=60 * 60)
def get_price_history(ticker: str) -> pd.DataFrame:
    import yfinance as yf

    tk = yf.Ticker(ticker)
    hist = tk.history(start="1990-01-01", auto_adjust=True)
    if hist is None or hist.empty:
        return pd.DataFrame()
    hist = hist[["Close"]].copy()
    hist.index = pd.to_datetime(hist.index).tz_localize(None)
    return hist


# ---------------------------------------------------------------------------
# Helpers de formato / descarga
# ---------------------------------------------------------------------------
def fmt_date(x, lang: str = "es") -> str:
    """Fecha localizada: DD/MM/YYYY en español, YYYY-MM-DD en inglés."""
    if isinstance(x, str):
        return x
    if pd.isna(x):
        return ""
    fmt = "%d/%m/%Y" if lang == "es" else "%Y-%m-%d"
    return pd.Timestamp(x).strftime(fmt)


def iso_date(x) -> str:
    """Fecha ISO estable, para nombres de fichero (sin barras)."""
    if isinstance(x, str):
        return x
    if pd.isna(x):
        return ""
    return pd.Timestamp(x).strftime("%Y-%m-%d")


def date_fmt_widget(lang: str) -> str:
    """Formato para el widget st.date_input según idioma."""
    return "DD/MM/YYYY" if lang == "es" else "YYYY-MM-DD"


def date_col_format(lang: str) -> str:
    """Formato de visualización para columnas de fecha (st.column_config.DateColumn).

    Las columnas se mantienen como fechas reales (datetime) para que la ordenación
    sea cronológica; este formato solo cambia cómo se muestran.
    """
    return "DD/MM/YYYY" if lang == "es" else "YYYY-MM-DD"


def entry_label(entry, t, lang: str = "es") -> str:
    if entry == "before1990":
        return t("f1_before_1990")
    return fmt_date(entry, lang)


def df_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Data") -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return buf.getvalue()


def download_button(df: pd.DataFrame, filename: str, label: str, key: str):
    st.download_button(
        label=label,
        data=df_to_excel_bytes(df),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key,
    )


def newsletter_callout(t):
    st.markdown(
        f"""
        <div class="q4a-news">
            <h4>{t('newsletter_title')}</h4>
            <p>{t('newsletter_text')}</p>
            <a href="{sub_url('hero')}" target="_blank" rel="noopener">{t('newsletter_button')}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def newsletter_cta(t, source: str):
    """CTA compacto contextual (una línea + botón), en el momento de máximo interés."""
    st.markdown(
        f"""
        <div class="q4a-cta">
            <span class="txt">{t('cta_inline')}</span>
            <a href="{sub_url(source)}" target="_blank" rel="noopener">{t('newsletter_button')}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Gráfico de precio con marcadores de índice
# ---------------------------------------------------------------------------
def build_price_chart(hist: pd.DataFrame, summary: dict, t) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            name=t("f1_price"),
            line=dict(color=ORANGE, width=2),
            hovertemplate="%{x|%Y-%m-%d}<br>%{y:.2f} $<extra></extra>",
        )
    )

    def _iso(x) -> str:
        return pd.Timestamp(x).strftime("%Y-%m-%d")

    x_min = _iso(hist.index.min())
    x_max = _iso(hist.index.max())
    index_colors = {"SPX": ORANGE, "NDX": BLUE}
    # Posición vertical de la etiqueta (paper coords) por índice, para no solaparse.
    y_anno = {"SPX": 0.98, "NDX": 0.06}

    def _vline(x_iso, color, dash, text):
        fig.add_shape(
            type="line", x0=x_iso, x1=x_iso, xref="x", y0=0, y1=1, yref="paper",
            line=dict(color=color, width=1.4, dash=dash),
        )
        fig.add_annotation(
            x=x_iso, xref="x", y=y_anno[key], yref="paper", text=text,
            showarrow=False, font=dict(color=color, size=11),
            bgcolor="rgba(10,20,40,.75)", xanchor="left", yanchor="middle",
        )

    for key, color in index_colors.items():
        label = D.INDEX_META[key]["label"]
        for start, end in summary.get(key, []):
            # Sombreado del periodo de pertenencia.
            rect_start = x_min if start == "before1990" else _iso(start)
            rect_end = x_max if end is None else _iso(end)
            fig.add_shape(
                type="rect", x0=rect_start, x1=rect_end, xref="x",
                y0=0, y1=1, yref="paper", fillcolor=color, opacity=0.07,
                line_width=0, layer="below",
            )
            # Marca de entrada.
            if start == "before1990":
                fig.add_annotation(
                    x=x_min, xref="x", y=y_anno[key], yref="paper",
                    text=f"{label}: {t('f1_before_1990')}", showarrow=False,
                    font=dict(color=color, size=11), bgcolor="rgba(10,20,40,.75)",
                    xanchor="left", yanchor="middle",
                )
            elif start is not None:
                _vline(_iso(start), color, "solid", f"{label} ▲ {t('f1_entered')}")
            # Marca de salida.
            if end is not None:
                _vline(_iso(end), color, "dot", f"{label} ▼ {t('f1_exited')}")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=520,
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(gridcolor="rgba(169,180,196,.12)", rangeslider=dict(visible=False)),
        yaxis=dict(
            gridcolor="rgba(169,180,196,.12)",
            title=t("f1_price") + " ($)",
            type="log",  # escala logarítmica (mejor para ver rentabilidad a largo plazo)
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------
def view_ticker(t, lang):
    st.subheader(t("f1_header"))
    st.caption(t("f1_intro"))

    data = get_data()
    live = get_live_tickers()

    col1, col2 = st.columns([2, 1])
    with col1:
        options = [t("f1_none")] + live["Label"].tolist()
        chosen_label = st.selectbox(t("f1_select"), options, index=0)
    with col2:
        free = st.text_input(t("f1_free"), value="", help=t("f1_free_help")).strip()

    ticker = None
    if free:
        ticker = D.resolve_ticker(get_data(), free)
    elif chosen_label and chosen_label != t("f1_none"):
        ticker = chosen_label.split(" | ")[0].strip()

    if not ticker:
        st.info(t("f1_empty"))
        return

    summary = D.ticker_membership_summary(data, ticker)
    display_name = summary["name"] if summary["exists"] else ticker

    st.markdown(f"### {ticker} | {display_name}")

    # CTA entre la fila de selección del ticker y el gráfico.
    newsletter_cta(t, "f1_ticker")

    # ¿Pertenece actualmente a algún índice? (un periodo abierto = sigue dentro)
    current_member = any(
        end is None for key in ("SPX", "NDX") for _, end in summary.get(key, [])
    )

    # ¿Es un ticker deslistado? -> no consultamos Yahoo.
    is_delisted = D.is_delisted_ticker(ticker)
    # Delistado también si aparece en la hoja de deslistados con ese símbolo base.
    delist_df = data["delisting"]
    delist_row = delist_df[delist_df["Ticker"].str.upper() == ticker.upper()]

    if is_delisted:
        st.warning(t("f1_delisted_warning"))
    else:
        try:
            hist = get_price_history(D.base_ticker(ticker))
        except Exception:
            hist = pd.DataFrame()
        if hist is not None and not hist.empty:
            # Alerta: se muestra el gráfico igualmente, pero avisamos si no es miembro actual.
            if not current_member:
                st.info(t("f1_not_current"))
            st.plotly_chart(
                build_price_chart(hist, summary, t),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            st.warning(t("f1_no_price"))

    # Resumen textual de pertenencia.
    st.markdown(f"#### {t('f1_membership')}")
    c1, c2 = st.columns(2)
    for col, key in [(c1, "SPX"), (c2, "NDX")]:
        with col:
            label = D.INDEX_META[key]["label"]
            spells = summary.get(key, [])
            st.markdown(f"**{label}**")
            if not spells:
                st.markdown(f"<span style='color:{MUTED}'>{t('f1_never')}</span>", unsafe_allow_html=True)
                continue
            for start, end in spells:
                start_txt = t("f1_before_1990") if start == "before1990" else fmt_date(start, lang)
                end_txt = t("f1_still_in") if end is None else fmt_date(end, lang)
                in_pill = f"<span class='q4a-pill in'>{t('f1_entered')}: {start_txt}</span>"
                out_pill = f"<span class='q4a-pill out'>{t('f1_exited')}: {end_txt}</span>"
                st.markdown(f"{in_pill} {out_pill}", unsafe_allow_html=True)

    if not delist_row.empty:
        d = delist_row.iloc[0]["Delisting Date"]
        st.info(f"🪦  {t('f1_delist_date')}: **{fmt_date(d, lang)}**")


def view_constituents(t, lang, index_key):
    st.subheader(t("f2_header"))
    data = get_data()
    df = data[index_key]
    index_label = D.INDEX_META[index_key]["label"]

    as_of = st.date_input(
        t("f2_date"),
        value=min(DB_MAX, dt.date(2020, 6, 15)),
        min_value=DB_MIN,
        max_value=DB_MAX,
        format=date_fmt_widget(lang),
        help=t("date_before_min"),
    )

    result = D.constituents_on(df, pd.Timestamp(as_of))

    st.markdown(
        f"""<div class="q4a-metric">
            <div class="val">{len(result)}</div>
            <div class="lbl">{t('f2_count').format(index=index_label, n=len(result), date=fmt_date(as_of, lang))}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    if result.empty:
        st.info(t("f2_empty"))
        return

    cols = t("f2_table_cols")
    delist_map = dict(zip(data["delisting"]["Ticker"], data["delisting"]["Delisting Date"]))

    # Fecha de incorporación como fecha real -> ordenación cronológica correcta al
    # clicar la cabecera. Los miembros "antes de 1990" se representan con la fecha de
    # inicio de la base (1990-01-02): son los más antiguos, así ordenan al principio.
    screen = result[["Ticker", "Name"]].copy()
    screen["Entry"] = pd.to_datetime(
        result["Entry"].apply(lambda e: D.DB_START if e == "before1990" else pd.Timestamp(e))
    )
    # Fecha de deslistado: texto (vacío si sigue cotizando). Se usa texto en vez de
    # columna de fecha porque Streamlit muestra "None" en las celdas nulas.
    screen["Delisting"] = result["Ticker"].map(delist_map).apply(
        lambda d: fmt_date(d, lang) if pd.notna(d) else ""
    )

    # Botón de descarga (izq.) + CTA (der.) en la misma fila, entre el número y la tabla.
    download = screen.rename(columns=cols)
    dcol, ctacol = st.columns([1, 2.6])
    with dcol:
        download_button(
            download,
            filename=f"{index_key}_constituents_{iso_date(as_of)}.xlsx",
            label=t("download_xlsx"),
            key="dl_f2",
        )
    with ctacol:
        newsletter_cta(t, "f2_constituents")

    date_fmt = date_col_format(lang)
    st.dataframe(
        screen,
        width="stretch",
        hide_index=True,
        height=520,
        column_config={
            "Ticker": st.column_config.TextColumn(cols["Ticker"]),
            "Name": st.column_config.TextColumn(cols["Name"]),
            "Entry": st.column_config.DateColumn(cols["Entry"], format=date_fmt),
            "Delisting": st.column_config.TextColumn(cols["Delisting"]),
        },
    )


def view_changes(t, lang, index_key):
    st.subheader(t("f3_header"))
    data = get_data()
    df = data[index_key]

    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input(
            t("f3_start"), value=dt.date(2024, 1, 1),
            min_value=DB_MIN, max_value=DB_MAX, format=date_fmt_widget(lang), key="f3_start",
        )
    with c2:
        end = st.date_input(
            t("f3_end"), value=min(DB_MAX, dt.date(2024, 12, 31)),
            min_value=DB_MIN, max_value=DB_MAX, format=date_fmt_widget(lang), key="f3_end",
        )

    if start > end:
        st.error(t("f3_bad_range"))
        return

    entries, exits = D.changes_in_range(df, pd.Timestamp(start), pd.Timestamp(end))
    cols = t("f3_table_cols")
    date_fmt = date_col_format(lang)
    delist_map = dict(zip(data["delisting"]["Ticker"], data["delisting"]["Delisting Date"]))

    def _with_delisting(frame: pd.DataFrame) -> pd.DataFrame:
        out = frame[["Ticker", "Name", "Date"]].copy()
        # Fecha de deslistado como texto (vacío si sigue cotizando) para evitar "None".
        out["Delisting"] = out["Ticker"].map(delist_map).apply(
            lambda d: fmt_date(d, lang) if pd.notna(d) else ""
        )
        return out

    # Todas las columnas con el mismo ancho.
    change_cfg = {
        "Ticker": st.column_config.TextColumn(cols["Ticker"], width="medium"),
        "Name": st.column_config.TextColumn(cols["Name"], width="medium"),
        "Date": st.column_config.DateColumn(cols["Date"], format=date_fmt, width="medium"),
        "Delisting": st.column_config.TextColumn(cols["Delisting"], width="medium"),
    }

    # Descarga (izq.) + CTA (der.) en la misma fila, entre las fechas y la cabecera de Entradas.
    if not entries.empty or not exits.empty:
        combined = pd.concat(
            [
                entries.assign(**{"Type": "Entry"}),
                exits.assign(**{"Type": "Exit"}),
            ],
            ignore_index=True,
        )
        combined["Delisting"] = combined["Ticker"].map(delist_map).apply(
            lambda d: fmt_date(d, lang) if pd.notna(d) else ""
        )
        dcol, ctacol = st.columns([1, 2.6])
        with dcol:
            download_button(
                combined[["Type", "Ticker", "Name", "Date", "Delisting"]],
                filename=f"{index_key}_changes_{iso_date(start)}_{iso_date(end)}.xlsx",
                label=t("download_xlsx"),
                key="dl_f3",
            )
        with ctacol:
            newsletter_cta(t, "f3_changes")
    else:
        newsletter_cta(t, "f3_changes")

    # Entradas primero (por fecha de incorporación), luego salidas (por fecha de salida).
    st.markdown(f"#### {t('f3_entries').format(n=len(entries))}")
    if entries.empty:
        st.info(t("f3_none_entries"))
    else:
        st.dataframe(
            _with_delisting(entries),
            width="stretch", hide_index=True, column_config=change_cfg,
        )

    st.markdown(f"#### {t('f3_exits').format(n=len(exits))}")
    if exits.empty:
        st.info(t("f3_none_exits"))
    else:
        st.dataframe(
            _with_delisting(exits),
            width="stretch", hide_index=True, column_config=change_cfg,
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
LANG_OPTS = {"🇪🇸 ES": "es", "🇬🇧 EN": "en"}


def main():
    inject_css()

    # --- Selector de idioma (arriba a la derecha, formato ES | EN) ---
    _, lang_col = st.columns([4, 1.4])
    with lang_col:
        sel = st.segmented_control(
            "lang",
            options=list(LANG_OPTS.keys()),
            default="🇪🇸 ES",
            label_visibility="collapsed",
            key="lang_sel",
        )
    lang = LANG_OPTS.get(sel, "es")
    t = make_translator(lang)

    # --- Newsletter arriba del todo ---
    newsletter_callout(t)

    # --- Cabecera ---
    st.markdown(
        f"""<div class="q4a-hero-title">{t('app_title')}</div>
        <p class="q4a-hero-sub">{t('app_subtitle')}</p>
        <div class="q4a-update">{t('db_updated').format(date=as_of_str(lang))}</div>
        <hr class="q4a-accent-rule"/>""",
        unsafe_allow_html=True,
    )

    # --- Sidebar (logo + navegación) ---
    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width="stretch")
        st.markdown(f"**{t('choose_action')}**")
        action = st.radio(
            t("navigation"),
            options=["ticker", "constituents", "changes"],
            format_func=lambda a: {
                "ticker": t("action_ticker"),
                "constituents": t("action_constituents"),
                "changes": t("action_changes"),
            }[a],
            label_visibility="collapsed",
        )

        index_key = None
        if action in ("constituents", "changes"):
            index_key = st.radio(
                t("choose_index"),
                options=["SPX", "NDX"],
                format_func=lambda k: D.INDEX_META[k]["label"],
                horizontal=True,
            )

    # --- Vista según acción ---
    if action == "ticker":
        view_ticker(t, lang)
    elif action == "constituents":
        view_constituents(t, lang, index_key)
    elif action == "changes":
        view_changes(t, lang, index_key)

    # --- Footer ---
    st.markdown(f"<div class='q4a-footer'>{t('footer')}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
