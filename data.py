"""
Capa de datos para Quant4all Index Roster.

Lee el Excel `Historical_Index_Constituent.xlsx` (pestañas SPX, NDX y
"Delisting Date") y expone la lógica de pertenencia histórica a los índices.

Formato de las pestañas SPX / NDX (formato largo por eventos):
    Ticker | Name | Date/Time | InSPX (ó InNDX)
Cada fila es una fecha de cambio de estado. El estado de pertenencia en una
fecha X es el flag de la última fila con fecha <= X.
    0 -> 1 : entrada al índice.
    1 -> 0 : salida del índice (en la fecha donde aparece el 0).
Si la primera fila de un ticker es 1 en 1990-01-02 -> "incorporada antes de 1990".
Los tickers deslistados llevan el sufijo "-Delisted"; el mismo símbolo lo han
usado empresas distintas a lo largo del tiempo, por eso el sufijo desambigua.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
XLSX_PATH = BASE_DIR / "Historical_Index_Constituent.xlsx"

# Primera fecha registrada en la base de datos.
DB_START = pd.Timestamp("1990-01-02")

# Metadatos de cada índice.
INDEX_META = {
    "SPX": {"flag": "InSPX", "label": "S&P 500"},
    "NDX": {"flag": "InNDX", "label": "Nasdaq 100"},
}

DELISTED_SUFFIX = "-Delisted"


def _load_index_sheet(sheet: str, flag_col: str) -> pd.DataFrame:
    """Carga y normaliza una pestaña de índice a columnas: Ticker, Name, Date, Flag."""
    df = pd.read_excel(
        XLSX_PATH, sheet_name=sheet, usecols=["Ticker", "Name", "Date/Time", flag_col]
    )
    df = df.rename(columns={flag_col: "Flag", "Date/Time": "Date"})

    # Elimina filas sin ticker (filas vacías al final de la hoja).
    df = df.dropna(subset=["Ticker"])
    df["Ticker"] = df["Ticker"].astype(str).str.strip()
    df = df[df["Ticker"] != ""]

    df["Name"] = df["Name"].astype(str).str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Flag vacío (p.ej. YELLQ) -> 0 (no miembro), para que nunca rompa cálculos.
    df["Flag"] = pd.to_numeric(df["Flag"], errors="coerce").fillna(0).astype(int)

    df = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    return df


def load_delisting() -> pd.DataFrame:
    """Carga la pestaña de deslistados: Ticker -> Name, Delisting Date."""
    df = pd.read_excel(
        XLSX_PATH, sheet_name="Delisting Date", usecols=["Ticker", "Name", "Delisting Date"]
    )
    df = df.dropna(subset=["Ticker"])
    df["Ticker"] = df["Ticker"].astype(str).str.strip()
    df = df[df["Ticker"] != ""]
    df["Name"] = df["Name"].astype(str).str.strip()
    df["Delisting Date"] = pd.to_datetime(df["Delisting Date"], errors="coerce")
    return df.reset_index(drop=True)


def load_all() -> dict:
    """Carga todo el dataset. Devuelve un dict con dataframes por índice y deslistados."""
    data = {}
    for key, meta in INDEX_META.items():
        data[key] = _load_index_sheet(key, meta["flag"])
    data["delisting"] = load_delisting()
    return data


# ---------------------------------------------------------------------------
# Utilidades de nombre / ticker
# ---------------------------------------------------------------------------
def is_delisted_ticker(ticker: str) -> bool:
    return DELISTED_SUFFIX.lower() in str(ticker).lower()


def base_ticker(ticker: str) -> str:
    """Quita el sufijo -Delisted para obtener el símbolo real (uso en Yahoo)."""
    t = str(ticker)
    if t.lower().endswith(DELISTED_SUFFIX.lower()):
        return t[: -len(DELISTED_SUFFIX)]
    return t


def resolve_ticker(data: dict, raw: str) -> str:
    """
    Resuelve el texto introducido por el usuario al ticker canónico de la base
    (respetando mayúsculas/minúsculas del sufijo -Delisted). Si no hay match,
    devuelve el texto en mayúsculas para intentarlo contra Yahoo Finance.
    """
    raw_s = str(raw).strip()
    if not raw_s:
        return raw_s
    target = raw_s.upper()
    for key in list(INDEX_META) + ["delisting"]:
        for tk in data[key]["Ticker"].unique():
            if str(tk).upper() == target:
                return tk
    return target


def latest_name(df: pd.DataFrame, ticker: str) -> str:
    sub = df[df["Ticker"] == ticker]
    if sub.empty:
        return ticker
    return sub.sort_values("Date")["Name"].iloc[-1]


# ---------------------------------------------------------------------------
# Lógica de pertenencia
# ---------------------------------------------------------------------------
def compute_spells(df: pd.DataFrame, ticker: str) -> list[tuple]:
    """
    Devuelve la lista de periodos (spells) de pertenencia de un ticker.

    Cada elemento es (start, end) donde:
        start: pd.Timestamp con la fecha de entrada, o la cadena "before1990"
               si el ticker ya era miembro en 1990-01-02.
        end:   pd.Timestamp con la fecha de salida, o None si sigue dentro.
    """
    sub = df[df["Ticker"] == ticker].sort_values("Date")
    if sub.empty:
        return []

    spells: list[tuple] = []
    cur_state = 0
    start = None

    for i, (_, row) in enumerate(sub.iterrows()):
        d = pd.Timestamp(row["Date"])
        f = int(row["Flag"])
        if i == 0:
            cur_state = f
            if f == 1:
                start = "before1990" if d == DB_START else d
            continue
        if f != cur_state:
            if f == 1:  # entrada
                start = d
            else:  # salida
                spells.append((start, d))
                start = None
            cur_state = f

    if cur_state == 1:
        spells.append((start, None))  # sigue dentro

    return spells


def entry_date_on(df: pd.DataFrame, ticker: str, as_of: pd.Timestamp):
    """
    Fecha de incorporación del periodo de pertenencia que contiene `as_of`.

    Devuelve pd.Timestamp, la cadena "before1990", o None si no era miembro.
    """
    as_of = pd.Timestamp(as_of)
    for start, end in compute_spells(df, ticker):
        start_date = DB_START if start == "before1990" else start
        end_date = end if end is not None else pd.Timestamp.max
        if start_date <= as_of < end_date:
            return start
    return None


def constituents_on(df: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """
    Constituyentes del índice en la fecha `as_of`.

    Devuelve un dataframe con: Ticker, Name, Entry (Timestamp o "before1990"),
    ordenado alfabéticamente por Ticker.
    """
    as_of = pd.Timestamp(as_of)
    sub = df[df["Date"] <= as_of]
    if sub.empty:
        return pd.DataFrame(columns=["Ticker", "Name", "Entry"])

    # Última fila (más reciente) por ticker hasta la fecha.
    idx = sub.groupby("Ticker")["Date"].idxmax()
    last = df.loc[idx]
    members = last[last["Flag"] == 1]

    rows = []
    for ticker in members["Ticker"]:
        rows.append(
            {
                "Ticker": ticker,
                "Name": latest_name(df, ticker),
                "Entry": entry_date_on(df, ticker, as_of),
            }
        )
    out = pd.DataFrame(rows, columns=["Ticker", "Name", "Entry"])
    return out.sort_values("Ticker", key=lambda s: s.str.lower()).reset_index(drop=True)


def changes_in_range(
    df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Entradas y salidas ocurridas en el rango [start, end] (inclusive).

    Devuelve (entradas, salidas), cada uno con columnas Ticker, Name, Date,
    ordenados por fecha (entrada/salida) y, a igualdad, por ticker.

    Una entrada es una transición 0->1, o la primera aparición de un ticker
    ya como miembro en una fecha posterior a 1990-01-02 (p.ej. KHC por fusión).
    Una salida es una transición 1->0.
    """
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    d = df.sort_values(["Ticker", "Date"]).copy()
    d["Prev"] = d.groupby("Ticker")["Flag"].shift(1)

    # Transiciones (hay fila anterior con flag distinto).
    trans = d[d["Prev"].notna() & (d["Flag"] != d["Prev"])]
    entries = trans[trans["Flag"] == 1].copy()
    exits = trans[trans["Flag"] == 0].copy()

    # Primeras apariciones ya como miembro en fecha > DB_START (nacidas dentro
    # del índice por fusión/spin-off): cuentan como entrada en esa fecha.
    first_rows = d.groupby("Ticker", as_index=False).first()
    born_in = first_rows[(first_rows["Flag"] == 1) & (first_rows["Date"] > DB_START)]
    entries = pd.concat([entries, born_in], ignore_index=True)

    def _filter(frame: pd.DataFrame) -> pd.DataFrame:
        m = frame[(frame["Date"] >= start) & (frame["Date"] <= end)]
        m = m[["Ticker", "Name", "Date"]].drop_duplicates()
        # Orden por defecto: por fecha (entrada/salida) y, a igualdad, por ticker.
        return m.sort_values(
            ["Date", "Ticker"], key=lambda s: s.str.lower() if s.name == "Ticker" else s
        ).reset_index(drop=True)

    return _filter(entries), _filter(exits)


def live_tickers(data: dict) -> pd.DataFrame:
    """
    Tickers 'vivos' (no deslistados) presentes en cualquiera de los índices,
    para el desplegable de la consulta con Yahoo Finance.

    Devuelve dataframe: Ticker, Name, Label ("TICKER — Name"), ordenado por ticker.
    """
    frames = []
    for key in INDEX_META:
        df = data[key]
        live = df[~df["Ticker"].apply(is_delisted_ticker)]
        for ticker in live["Ticker"].unique():
            frames.append({"Ticker": ticker, "Name": latest_name(df, ticker)})
    out = pd.DataFrame(frames).drop_duplicates(subset=["Ticker"])
    out["Label"] = out["Ticker"] + " | " + out["Name"]
    return out.sort_values("Ticker", key=lambda s: s.str.lower()).reset_index(drop=True)


def ticker_membership_summary(data: dict, ticker: str) -> dict:
    """
    Resumen de pertenencia de un ticker en ambos índices, para la Funcionalidad 1.

    Devuelve dict: {"SPX": [spells], "NDX": [spells], "exists": bool,
                    "delisted": bool, "name": str}
    """
    result = {"SPX": [], "NDX": [], "exists": False, "delisted": False, "name": ticker}
    for key in INDEX_META:
        df = data[key]
        if ticker in set(df["Ticker"]):
            result["exists"] = True
            result["name"] = latest_name(df, ticker)
            result[key] = compute_spells(df, ticker)
    result["delisted"] = is_delisted_ticker(ticker)
    return result
