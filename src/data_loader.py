"""
data_loader.py — NEMOSIS interface for the NEM DER Impact Analyser.

This is the only module that touches pandas. All public functions convert
NEMOSIS DataFrames to custom domain types immediately before returning.

Timestamps are in AEST (UTC+10), non-daylight-saving.
SETTLEMENTDATE is the END of the dispatch interval.

NEMOSIS date format: 'YYYY/MM/DD HH:MM:SS'
"""

from pathlib import Path

import nemosis
import pandas as pd

from src.models import (
    PriceRecord,
    PriceSeries,
    ScadaRecord,
    ScadaSeries,
    RooftopPVRecord,
    RooftopPVSeries,
)

# Resolve cache dir relative to this file (src/ -> repo root -> data/cache/)
_CACHE_DIR = str(Path(__file__).parent.parent / "data" / "cache")


def format_date(dt) -> str:
    """Convert a date-like value to the NEMOSIS format 'YYYY/MM/DD HH:MM:SS'."""
    return pd.Timestamp(dt).strftime("%Y/%m/%d %H:%M:%S")


def load_dispatch_price(
    start: str,
    end: str,
    region: str = "SA1",
) -> PriceSeries:
    """
    Pull spot price data from DISPATCHPRICE for the given date range and region.

    Parameters
    ----------
    start, end : str
        Date strings in any format pandas can parse (e.g. '2023-01-01').
    region : str
        NEM region ID (default 'SA1').

    Returns
    -------
    PriceSeries
    """
    df = nemosis.dynamic_data_compiler(
        format_date(start),
        format_date(end),
        "DISPATCHPRICE",
        _CACHE_DIR,
    )
    df = df[df["REGIONID"] == region][["SETTLEMENTDATE", "REGIONID", "RRP"]].copy()
    df["SETTLEMENTDATE"] = pd.to_datetime(df["SETTLEMENTDATE"])
    df = df.sort_values("SETTLEMENTDATE")

    records = [
        PriceRecord(settlementdate=ts.to_pydatetime(), regionid=rid, rrp=float(rrp))
        for ts, rid, rrp in zip(df["SETTLEMENTDATE"], df["REGIONID"], df["RRP"])
    ]
    return PriceSeries(records)


def load_unit_scada(
    start: str,
    end: str,
    region: str = "SA1",
) -> ScadaSeries:
    """
    Pull actual generator output from DISPATCH_UNIT_SCADA, filtered to a region.

    DISPATCH_UNIT_SCADA has no REGIONID column — region filtering is done by
    joining with DUDETAILSUMMARY (static generator metadata table).

    Parameters
    ----------
    start, end : str
        Date strings in any format pandas can parse.
    region : str
        NEM region ID (default 'SA1').

    Returns
    -------
    ScadaSeries
    """
    dudetail = nemosis.static_table("DUDETAILSUMMARY", _CACHE_DIR)
    region_duids = set(dudetail[dudetail["REGIONID"] == region]["DUID"].unique())

    df = nemosis.dynamic_data_compiler(
        format_date(start),
        format_date(end),
        "DISPATCH_UNIT_SCADA",
        _CACHE_DIR,
    )
    df = df[df["DUID"].isin(region_duids)][
        ["SETTLEMENTDATE", "DUID", "SCADAVALUE"]
    ].copy()
    df["SETTLEMENTDATE"] = pd.to_datetime(df["SETTLEMENTDATE"])
    df = df.sort_values("SETTLEMENTDATE")

    records = [
        ScadaRecord(settlementdate=ts.to_pydatetime(), duid=duid, scadavalue=float(val))
        for ts, duid, val in zip(df["SETTLEMENTDATE"], df["DUID"], df["SCADAVALUE"])
    ]
    return ScadaSeries(records)


def load_rooftop_pv(
    start: str,
    end: str,
    region: str = "SA1",
) -> RooftopPVSeries:
    """
    Pull AEMO's estimated rooftop PV generation from ROOFTOP_PV_ACTUAL.

    Parameters
    ----------
    start, end : str
        Date strings in any format pandas can parse.
    region : str
        NEM region ID (default 'SA1').

    Returns
    -------
    RooftopPVSeries
    """
    df = nemosis.dynamic_data_compiler(
        format_date(start),
        format_date(end),
        "ROOFTOP_PV_ACTUAL",
        _CACHE_DIR,
    )
    # ROOFTOP_PV_ACTUAL columns: INTERVAL_DATETIME, REGIONID, POWER, QI, TYPE, LASTCHANGED
    # TYPE has two values: 'MEASUREMENT' (actuals) and 'SATELLITE' (estimates) — keep actuals only
    df = df[(df["REGIONID"] == region) & (df["TYPE"] == "MEASUREMENT")].copy()
    df = df[["INTERVAL_DATETIME", "REGIONID", "POWER"]].copy()
    df["INTERVAL_DATETIME"] = pd.to_datetime(df["INTERVAL_DATETIME"])
    df = df.sort_values("INTERVAL_DATETIME")

    records = [
        RooftopPVRecord(settlementdate=ts.to_pydatetime(), regionid=rid, power_mw=float(mw))
        for ts, rid, mw in zip(df["INTERVAL_DATETIME"], df["REGIONID"], df["POWER"])
    ]
    return RooftopPVSeries(records)
