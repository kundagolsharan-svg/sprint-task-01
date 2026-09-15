"""Normalisation helpers shared by the loader and validator."""

import re
from datetime import datetime

import pandas as pd


def normalize_ticker(value: object) -> str | None:
    if pd.isna(value):
        return None
    ticker = re.sub(r"[^A-Z0-9&.-]", "", str(value).strip().upper())
    return ticker or None


def normalize_year(value: object) -> int | str | None:
    if pd.isna(value):
        return None
    if isinstance(value, (datetime, pd.Timestamp)):
        return int(value.year)
    text = str(value).strip().upper()
    if text == "TTM":
        return "TTM"
    match = re.search(r"(19|20)\d{2}", text)
    if match:
        return int(match.group(0))
    match = re.search(r"\b(\d{2})\b", text)
    if match:
        year = int(match.group(1))
        return 2000 + year if year < 50 else 1900 + year
    return None


def clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Remove the report title row and normalize blank Excel headers."""
    frame = frame.copy()
    if len(frame.columns) and str(frame.columns[0]).lower().startswith(("bluestock", "mkt fintech")):
        headers = frame.iloc[0].tolist()
        frame = frame.iloc[1:].copy()
        frame.columns = headers
    frame = frame.loc[:, ~frame.columns.astype(str).str.startswith("Unnamed")]
    frame.columns = [str(column).strip().lower().replace(" ", "_") for column in frame.columns]
    return frame.reset_index(drop=True)