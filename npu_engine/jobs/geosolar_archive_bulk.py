"""
Multi-decade geosolar archive bulk fetch (1973-01-01 .. 2024-12-31).

Fetches Kp, Dst, seismic, tide for the full 1973–2024 window and writes
per-decade Parquet files under datasets/geosolar/archive/<source>/.

2025 data lives in the 2025 pilot files (kp_2025.parquet, dst_2025.parquet,
seismic_2025_M4plus.parquet, tide_sf_2025_hourly.parquet) — those are NOT
re-fetched or merged here. Merge at analysis time.

Decade partitioning:
    kp_1970s.parquet   1973-01-01 .. 1979-12-31  (7 years)
    kp_1980s.parquet   1980-01-01 .. 1989-12-31
    kp_1990s.parquet   1990-01-01 .. 1999-12-31
    kp_2000s.parquet   2000-01-01 .. 2009-12-31
    kp_2010s.parquet   2010-01-01 .. 2019-12-31
    kp_2020s.parquet   2020-01-01 .. 2024-12-31  (5 years; 2025 in pilot)

Same scheme for dst/, seismic/, tide/.

Resumability: if a decade Parquet exists and is non-zero size, it is skipped
unless --reset is passed. This lets us re-run after a partial failure
without re-fetching completed decades.

Run:
    /home/inahd/atlas_core/.venv-archive/bin/python -m npu_engine.jobs.geosolar_archive_bulk
    /home/inahd/atlas_core/.venv-archive/bin/python -m npu_engine.jobs.geosolar_archive_bulk --reset

Parsers reused from `geosolar_archive_pilot.py`:
    Kp fixed-width 62-char layout (yy mm dd BR bd K1..K8 Sum a1..a8 Ap Cp).
    Kyoto WDC-1 monthly Dst layout (header chars 0..19, 24×4-char hourly values).
    USGS ComCat CSV.
    NOAA CO-OPS hourly_height CSV.

Defensiveness:
    - per-year try/except; failures recorded in manifest, never abort
    - 9999/999 honored as missing-data flags (Dst)
    - all timestamps stored UTC
    - polite delays per source (0.5 s annual, 0.5 s monthly Dst, 1.0 s ComCat/COOPS)
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

# Reuse pilot's schemas + Dst monthly parser
from npu_engine.jobs.geosolar_archive_pilot import (
    KP_SCHEMA, DST_SCHEMA, SEIS_SCHEMA, TIDE_SCHEMA,
    UA, HEADERS,
    _parse_dst_file,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ARCHIVE_DIR = os.path.join(REPO_ROOT, "datasets", "geosolar", "archive")
REPORT_OUT = os.path.join(ARCHIVE_DIR, "BULK_REPORT_1973_2024.md")

START_YEAR = 1973
END_YEAR = 2024

DECADES: List[Tuple[str, int, int]] = [
    ("1970s", 1973, 1979),
    ("1980s", 1980, 1989),
    ("1990s", 1990, 1999),
    ("2000s", 2000, 2009),
    ("2010s", 2010, 2019),
    ("2020s", 2020, 2024),
]


def decade_for_year(year: int) -> Optional[str]:
    for name, lo, hi in DECADES:
        if lo <= year <= hi:
            return name
    return None


def decade_path(source: str, decade: str) -> str:
    if source == "seismic":
        return os.path.join(ARCHIVE_DIR, source, f"seismic_{decade}_M4plus.parquet")
    if source == "tide":
        return os.path.join(ARCHIVE_DIR, source, f"tide_sf_{decade}_hourly.parquet")
    return os.path.join(ARCHIVE_DIR, source, f"{source}_{decade}.parquet")


# ── Manifest ────────────────────────────────────────────────────

@dataclass
class SourceStat:
    name: str
    http_count: int = 0
    years_ok: List[int] = field(default_factory=list)
    years_failed: List[Tuple[int, str]] = field(default_factory=list)
    rows_total: int = 0
    rows_skipped: int = 0
    min_ts: Optional[pd.Timestamp] = None
    max_ts: Optional[pd.Timestamp] = None
    decade_rows: Dict[str, int] = field(default_factory=dict)
    decade_bytes: Dict[str, int] = field(default_factory=dict)
    gaps_over_7d: List[Tuple[str, str, str]] = field(default_factory=list)
    extras: dict = field(default_factory=dict)


# ── Common helpers ──────────────────────────────────────────────

def _ensure_dirs():
    for s in ("kp", "dst", "seismic", "tide"):
        os.makedirs(os.path.join(ARCHIVE_DIR, s), exist_ok=True)


def _existing_decade_paths(source: str) -> Dict[str, str]:
    out = {}
    for name, _lo, _hi in DECADES:
        p = decade_path(source, name)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            out[name] = p
    return out


def _coerce_dt_ns_utc(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, utc=True).astype("datetime64[ns, UTC]")


def _gaps_over(timestamps: pd.Series, threshold: pd.Timedelta, limit: int = 5) -> List[Tuple[str, str, str]]:
    if len(timestamps) < 2:
        return []
    s = timestamps.sort_values().reset_index(drop=True)
    diffs = s.diff()
    out = []
    for i, d in enumerate(diffs):
        if pd.notna(d) and d > threshold:
            out.append((str(s.iloc[i - 1]), str(s.iloc[i]), str(d)))
            if len(out) >= limit:
                break
    return out


def _write_decade(df: pd.DataFrame, schema: pa.Schema, out_path: str) -> int:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if len(df) == 0:
        empty = pa.Table.from_pylist([], schema=schema)
        pq.write_table(empty, out_path)
    else:
        # Cast timestamps to ns,UTC to match schema
        if "timestamp" in df.columns:
            df = df.copy()
            df["timestamp"] = _coerce_dt_ns_utc(df["timestamp"])
        table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
        pq.write_table(table, out_path)
    return os.path.getsize(out_path)


# ── (1) Kp ──────────────────────────────────────────────────────

KP_DIR_URL = "https://datapub.gfz-potsdam.de/download/10.5880.Kp.0001/Kp_definitive/"
KP_HOUR_STARTS = [0, 3, 6, 9, 12, 15, 18, 21]


def _list_kp_files() -> Dict[int, str]:
    """Return {year: filename} for all Kp_def<YYYY>.wdc files in the archive."""
    r = requests.get(KP_DIR_URL, headers=HEADERS, timeout=60)
    r.raise_for_status()
    out = {}
    for m in re.finditer(r'href="(Kp_def(\d{4})\.wdc)"', r.text):
        fname, year = m.group(1), int(m.group(2))
        out[year] = fname
    return out


def _parse_kp_text(text: str) -> Tuple[List[dict], int]:
    """GFZ Kp_def<YYYY>.wdc fixed-width parser (62-char data lines).

    cols 1-2 yy, 3-4 mm, 5-6 dd, 7-10 BR, 11-12 bd,
    13-28 8×Kp×10 (2 chars), 29-31 sum*10, 32-55 8×ap (3 chars),
    56-58 Ap, 59-62 Cp.
    """
    rows = []
    skipped = 0
    for ln in text.splitlines():
        if len(ln) < 58 or not ln[0:2].strip().isdigit():
            continue
        try:
            yy = int(ln[0:2])
            month = int(ln[2:4].strip())
            day = int(ln[4:6].strip())
            year = 2000 + yy if yy < 70 else 1900 + yy
            day_dt = datetime(year, month, day, tzinfo=timezone.utc)
            kp_field = ln[12:28]
            ap_field = ln[31:55]
            for i, hr in enumerate(KP_HOUR_STARTS):
                kp_raw = kp_field[i * 2:(i + 1) * 2].strip()
                ap_raw = ap_field[i * 3:(i + 1) * 3].strip()
                if not kp_raw or not ap_raw:
                    skipped += 1
                    continue
                try:
                    rows.append({
                        "timestamp": day_dt + timedelta(hours=hr),
                        "kp": int(kp_raw) / 10.0,
                        "ap": float(ap_raw),
                    })
                except ValueError:
                    skipped += 1
        except Exception:
            skipped += 1
    return rows, skipped


def run_kp(reset: bool, stat: SourceStat) -> None:
    print("[kp] starting")
    decades_done = {} if reset else _existing_decade_paths("kp")
    print(f"[kp] existing decades: {list(decades_done.keys())}")

    # Discover files
    try:
        kp_files = _list_kp_files()
        stat.http_count += 1
    except Exception as e:
        print(f"[kp] FATAL — directory listing failed: {e}")
        for y in range(START_YEAR, END_YEAR + 1):
            stat.years_failed.append((y, "directory listing failed"))
        return

    # Group years by decade
    decade_to_years = {name: [] for name, _, _ in DECADES}
    for name, lo, hi in DECADES:
        for y in range(lo, hi + 1):
            decade_to_years[name].append(y)

    for decade_name, _lo, _hi in DECADES:
        if decade_name in decades_done:
            stat.decade_bytes[decade_name] = os.path.getsize(decades_done[decade_name])
            try:
                t = pq.read_table(decades_done[decade_name])
                stat.decade_rows[decade_name] = len(t)
            except Exception:
                stat.decade_rows[decade_name] = -1
            print(f"[kp] {decade_name}: SKIP (already exists, "
                  f"{stat.decade_rows[decade_name]:,} rows)")
            continue

        rows: List[dict] = []
        for year in decade_to_years[decade_name]:
            if year not in kp_files:
                stat.years_failed.append((year, "no file in GFZ directory listing"))
                print(f"[kp]   {year}: no file")
                continue
            url = KP_DIR_URL + kp_files[year]
            try:
                r = requests.get(url, headers=HEADERS, timeout=60)
                stat.http_count += 1
                r.raise_for_status()
                yr_rows, sk = _parse_kp_text(r.text)
                rows.extend(yr_rows)
                stat.rows_skipped += sk
                stat.years_ok.append(year)
                print(f"[kp]   {year}: {len(yr_rows):,} rows ({sk} skipped)")
            except Exception as e:
                stat.years_failed.append((year, str(e)[:200]))
                print(f"[kp]   {year}: ERROR {e}")
            time.sleep(0.5)

        df = pd.DataFrame(rows)
        if len(df):
            df["timestamp"] = _coerce_dt_ns_utc(df["timestamp"])
            df["kp"] = df["kp"].astype("float32")
            df["ap"] = df["ap"].astype("float32")
            df = df.sort_values("timestamp").reset_index(drop=True)
            if stat.min_ts is None or df["timestamp"].min() < stat.min_ts:
                stat.min_ts = df["timestamp"].min()
            if stat.max_ts is None or df["timestamp"].max() > stat.max_ts:
                stat.max_ts = df["timestamp"].max()
            stat.gaps_over_7d.extend(_gaps_over(df["timestamp"], pd.Timedelta(days=7)))

        out = decade_path("kp", decade_name)
        size = _write_decade(df, KP_SCHEMA, out)
        stat.rows_total += len(df)
        stat.decade_rows[decade_name] = len(df)
        stat.decade_bytes[decade_name] = size
        print(f"[kp] {decade_name}: wrote {len(df):,} rows -> {out} ({size:,} bytes)")


# ── (2) Dst ─────────────────────────────────────────────────────

DST_PORTAL = "https://wdc.kugi.kyoto-u.ac.jp/dstdir/"
DST_FINAL_BASE = "https://wdc.kugi.kyoto-u.ac.jp/dst_final"
DST_PROVISIONAL_BASE = "https://wdc.kugi.kyoto-u.ac.jp/dst_provisional"
DST_REALTIME_BASE = "https://wdc.kugi.kyoto-u.ac.jp/dst_realtime"

# Kyoto's dst_final archive only serves dst<YYMM>.for.request files for
# 2000+; pre-2000 monthly pages embed the data inline in HTML <pre class="data">
# blocks. We need a different parser for those.
DST_FINAL_FORREQUEST_FROM = 2000


def _parse_dst_html_page(html: str, year: int, month: int) -> Tuple[List[dict], int]:
    """Parse a dst_final/<YYYYMM>/index.html page (pre-2000) where the data
    sits inline in a <pre class="data"> block. Each data line begins with the
    day-of-month and is followed by 24 hourly Dst values (whitespace-separated,
    with extra spacing every 8 values). 9999/999 honored as missing.
    """
    # Extract the <pre class="data"> block
    m = re.search(r'<pre[^>]*class="data"[^>]*>(.*?)</pre>', html, re.DOTALL | re.IGNORECASE)
    if not m:
        return [], 0
    block = m.group(1)
    rows: List[dict] = []
    skipped = 0
    seen_day_header = False
    int_re = re.compile(r"-?\d+")
    for ln in block.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("DAY"):
            seen_day_header = True
            continue
        if not seen_day_header:
            continue
        # First whitespace-delimited token is the day; the rest is the value
        # stream. Storm-condition rows pack 3-digit negatives without spaces
        # (e.g., "-130-151-151-147"), so we use a signed-integer regex on the
        # value portion rather than splitting on whitespace.
        parts = s.split(None, 1)
        if len(parts) < 2:
            continue
        try:
            day = int(parts[0])
        except ValueError:
            continue
        ints = int_re.findall(parts[1])
        if len(ints) < 24:
            continue  # malformed line, skip silently (not counted in skipped)
        try:
            day_dt = datetime(year, month, day, tzinfo=timezone.utc)
        except ValueError:
            skipped += 1
            continue
        for hr in range(24):
            try:
                val = float(ints[hr])
            except ValueError:
                skipped += 1
                continue
            if val in (9999.0, 999.0):
                skipped += 1
                continue
            rows.append({
                "timestamp": day_dt + timedelta(hours=hr),
                "dst_nT": val,
            })
    return rows, skipped


def _dst_cutoffs(stat: SourceStat) -> dict:
    """Parse the dstdir portal page to determine the date ranges
    served by final, provisional, realtime."""
    r = requests.get(DST_PORTAL, headers=HEADERS, timeout=30)
    stat.http_count += 1
    txt = r.text
    out = {}

    m = re.search(r"Final Dst index\s*\[\s*(\d{4})\s*-\s*(\d{4})\s*\]", txt)
    if m:
        out["final"] = (int(m.group(1)), int(m.group(2)))
    m = re.search(r"Provisional Dst index[^\[]*\[\s*(\d{4})/(\d{2})\s*-\s*(\d{4})/(\d{2})\s*\]",
                  txt, re.DOTALL)
    if m:
        out["provisional"] = (int(m.group(1)), int(m.group(2)),
                               int(m.group(3)), int(m.group(4)))
    return out


def _dst_url_for(year: int, month: int, cutoffs: dict) -> Tuple[Optional[str], str]:
    """Pick the right URL and parse-mode for a given month.

    Returns (url, mode) where mode is:
        'forreq'   — fetch dst<YYMM>.for.request, parse with _parse_dst_file
        'htmlpre'  — fetch index.html, parse <pre class="data"> with _parse_dst_html_page
    """
    yymm = f"{year % 100:02d}{month:02d}"
    fname_forreq = f"dst{yymm}.for.request"

    final = cutoffs.get("final")
    prov = cutoffs.get("provisional")

    if final and final[0] <= year <= final[1]:
        if year >= DST_FINAL_FORREQUEST_FROM:
            return (f"{DST_FINAL_BASE}/{year}{month:02d}/{fname_forreq}", "forreq")
        else:
            return (f"{DST_FINAL_BASE}/{year}{month:02d}/index.html", "htmlpre")
    if prov:
        py_lo, pm_lo, py_hi, pm_hi = prov
        ym = year * 100 + month
        if (py_lo * 100 + pm_lo) <= ym <= (py_hi * 100 + pm_hi):
            return (f"{DST_PROVISIONAL_BASE}/{year}{month:02d}/{fname_forreq}", "forreq")
    return (f"{DST_REALTIME_BASE}/{year}{month:02d}/{fname_forreq}", "forreq")


def run_dst(reset: bool, stat: SourceStat) -> None:
    print("[dst] starting")
    decades_done = {} if reset else _existing_decade_paths("dst")
    print(f"[dst] existing decades: {list(decades_done.keys())}")

    try:
        cutoffs = _dst_cutoffs(stat)
    except Exception as e:
        print(f"[dst] FATAL — cutoff page failed: {e}")
        cutoffs = {"final": (1957, 2020), "provisional": (2021, 1, 2025, 6)}
    stat.extras["cutoffs"] = cutoffs
    print(f"[dst] cutoffs: {cutoffs}")

    for decade_name, lo, hi in DECADES:
        if decade_name in decades_done:
            stat.decade_bytes[decade_name] = os.path.getsize(decades_done[decade_name])
            try:
                t = pq.read_table(decades_done[decade_name])
                stat.decade_rows[decade_name] = len(t)
            except Exception:
                stat.decade_rows[decade_name] = -1
            print(f"[dst] {decade_name}: SKIP ({stat.decade_rows[decade_name]:,} rows)")
            continue

        rows: List[dict] = []
        years_seen_ok = set()
        for year in range(lo, hi + 1):
            year_rows = 0
            year_skipped = 0
            year_ok = True
            for month in range(1, 13):
                url, mode = _dst_url_for(year, month, cutoffs)
                if url is None:
                    year_ok = False
                    continue
                try:
                    r = requests.get(url, headers=HEADERS, timeout=30)
                    stat.http_count += 1
                    # Kyoto's dst_final has irregular .for.request availability:
                    # 2001-2004 lack the .for.request file but the HTML page exists.
                    # Fall back to scraping <pre class="data"> from index.html.
                    if r.status_code == 404 and mode == "forreq" and url.endswith(".for.request"):
                        fallback_url = url.rsplit("/", 1)[0] + "/index.html"
                        r = requests.get(fallback_url, headers=HEADERS, timeout=30)
                        stat.http_count += 1
                        time.sleep(0.5)
                        mode = "htmlpre"
                    if r.status_code != 200:
                        year_ok = False
                        continue
                    if mode == "htmlpre":
                        mrows, sk = _parse_dst_html_page(r.text, year, month)
                    else:
                        mrows, sk = _parse_dst_file(r.text)
                    rows.extend(mrows)
                    stat.rows_skipped += sk
                    year_rows += len(mrows)
                    year_skipped += sk
                except Exception as e:
                    year_ok = False
                    stat.years_failed.append((year, f"{year}-{month:02d}: {str(e)[:150]}"))
                time.sleep(0.5)
            if year_ok and year_rows > 0:
                years_seen_ok.add(year)
            elif year_rows == 0:
                stat.years_failed.append((year, "no monthly files retrieved"))
            print(f"[dst]   {year}: {year_rows:,} rows ({year_skipped} skipped)")

        stat.years_ok.extend(sorted(years_seen_ok))

        df = pd.DataFrame(rows)
        if len(df):
            df["timestamp"] = _coerce_dt_ns_utc(df["timestamp"])
            df["dst_nT"] = df["dst_nT"].astype("float32")
            df = df.sort_values("timestamp").reset_index(drop=True)
            df = df.drop_duplicates(subset=["timestamp"]).reset_index(drop=True)
            if stat.min_ts is None or df["timestamp"].min() < stat.min_ts:
                stat.min_ts = df["timestamp"].min()
            if stat.max_ts is None or df["timestamp"].max() > stat.max_ts:
                stat.max_ts = df["timestamp"].max()
            stat.gaps_over_7d.extend(_gaps_over(df["timestamp"], pd.Timedelta(days=7)))

        out = decade_path("dst", decade_name)
        size = _write_decade(df, DST_SCHEMA, out)
        stat.rows_total += len(df)
        stat.decade_rows[decade_name] = len(df)
        stat.decade_bytes[decade_name] = size
        print(f"[dst] {decade_name}: wrote {len(df):,} rows -> {out} ({size:,} bytes)")


# ── (3) Seismic ─────────────────────────────────────────────────

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def _fetch_usgs_chunk(start: str, end: str) -> Tuple[pd.DataFrame, bool]:
    """Returns (df, ok). ok=False indicates a probable 'too many results' or HTTP error."""
    params = {
        "format": "csv",
        "starttime": start,
        "endtime": end,
        "minmagnitude": 4.0,
        "orderby": "time-asc",
    }
    r = requests.get(USGS_URL, params=params, headers=HEADERS, timeout=180)
    if r.status_code == 400:
        return pd.DataFrame(), False
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text)), True


def _fetch_seismic_year(year: int, stat: SourceStat) -> pd.DataFrame:
    """One year, single shot. Paginate quarterly if too many results."""
    df, ok = _fetch_usgs_chunk(f"{year}-01-01", f"{year}-12-31T23:59:59")
    stat.http_count += 1
    time.sleep(1.0)
    if not ok or len(df) == 0 or len(df) >= 19000:
        print(f"[seismic]     {year}: paginating quarterly (single-shot {len(df) if ok else 'failed'})")
        frames = []
        quarters = [
            (f"{year}-01-01", f"{year}-03-31T23:59:59"),
            (f"{year}-04-01", f"{year}-06-30T23:59:59"),
            (f"{year}-07-01", f"{year}-09-30T23:59:59"),
            (f"{year}-10-01", f"{year}-12-31T23:59:59"),
        ]
        for s, e in quarters:
            dfq, qok = _fetch_usgs_chunk(s, e)
            stat.http_count += 1
            if qok and len(dfq):
                frames.append(dfq)
            time.sleep(1.0)
        if frames:
            df = pd.concat(frames, ignore_index=True)
        else:
            df = pd.DataFrame()
    return df


def _normalize_seismic(raw: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    if len(raw) == 0:
        return pd.DataFrame(columns=[f.name for f in SEIS_SCHEMA]), 0
    out = pd.DataFrame()
    out["timestamp"] = pd.to_datetime(raw["time"], utc=True, errors="coerce")
    out["latitude"] = pd.to_numeric(raw["latitude"], errors="coerce").astype("float64")
    out["longitude"] = pd.to_numeric(raw["longitude"], errors="coerce").astype("float64")
    out["depth_km"] = pd.to_numeric(raw["depth"], errors="coerce").astype("float32")
    out["magnitude"] = pd.to_numeric(raw["mag"], errors="coerce").astype("float32")
    out["magType"] = raw["magType"].astype("string")
    out["place"] = raw["place"].astype("string")
    out["event_id"] = raw["id"].astype("string")
    bad = out["timestamp"].isna() | out["magnitude"].isna()
    skipped = int(bad.sum())
    out = out[~bad].copy()
    out = out.drop_duplicates(subset=["event_id"]).reset_index(drop=True)
    return out, skipped


def run_seismic(reset: bool, stat: SourceStat) -> None:
    print("[seismic] starting")
    decades_done = {} if reset else _existing_decade_paths("seismic")
    print(f"[seismic] existing decades: {list(decades_done.keys())}")

    decade_mag_bins: Dict[str, Dict[str, int]] = {}

    for decade_name, lo, hi in DECADES:
        if decade_name in decades_done:
            p = decades_done[decade_name]
            stat.decade_bytes[decade_name] = os.path.getsize(p)
            try:
                t = pq.read_table(p).to_pandas()
                stat.decade_rows[decade_name] = len(t)
                if "magnitude" in t.columns:
                    decade_mag_bins[decade_name] = _mag_bins(t["magnitude"])
            except Exception:
                stat.decade_rows[decade_name] = -1
            print(f"[seismic] {decade_name}: SKIP ({stat.decade_rows[decade_name]:,} rows)")
            continue

        frames = []
        for year in range(lo, hi + 1):
            try:
                raw = _fetch_seismic_year(year, stat)
                norm, skipped = _normalize_seismic(raw)
                stat.rows_skipped += skipped
                if len(norm):
                    frames.append(norm)
                    stat.years_ok.append(year)
                    print(f"[seismic]   {year}: {len(norm):,} rows ({skipped} skipped)")
                else:
                    stat.years_failed.append((year, "0 rows after normalize"))
                    print(f"[seismic]   {year}: 0 rows")
            except Exception as e:
                stat.years_failed.append((year, str(e)[:200]))
                print(f"[seismic]   {year}: ERROR {e}")

        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if len(df):
            df["timestamp"] = _coerce_dt_ns_utc(df["timestamp"])
            df = df.drop_duplicates(subset=["event_id"]).sort_values("timestamp").reset_index(drop=True)
            if stat.min_ts is None or df["timestamp"].min() < stat.min_ts:
                stat.min_ts = df["timestamp"].min()
            if stat.max_ts is None or df["timestamp"].max() > stat.max_ts:
                stat.max_ts = df["timestamp"].max()
            decade_mag_bins[decade_name] = _mag_bins(df["magnitude"])

        out = decade_path("seismic", decade_name)
        size = _write_decade(df, SEIS_SCHEMA, out)
        stat.rows_total += len(df)
        stat.decade_rows[decade_name] = len(df)
        stat.decade_bytes[decade_name] = size
        print(f"[seismic] {decade_name}: wrote {len(df):,} rows -> {out} ({size:,} bytes)")

    stat.extras["mag_bins"] = decade_mag_bins


def _mag_bins(mags: pd.Series) -> Dict[str, int]:
    m = pd.to_numeric(mags, errors="coerce")
    return {
        "M4.0-4.9": int(((m >= 4.0) & (m < 5.0)).sum()),
        "M5.0-5.9": int(((m >= 5.0) & (m < 6.0)).sum()),
        "M6.0-6.9": int(((m >= 6.0) & (m < 7.0)).sum()),
        "M7.0+":    int((m >= 7.0).sum()),
    }


# ── (4) Tide ────────────────────────────────────────────────────

COOPS_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
SF_STATION = "9414290"


def _fetch_coops_year(year: int) -> pd.DataFrame:
    params = {
        "product": "hourly_height",
        "application": "AtlasCore",
        "begin_date": f"{year}0101",
        "end_date":   f"{year}1231",
        "datum": "MLLW",
        "station": SF_STATION,
        "time_zone": "GMT",
        "units": "metric",
        "format": "csv",
    }
    r = requests.get(COOPS_URL, params=params, headers=HEADERS, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    if r.text.lstrip().lower().startswith("error"):
        raise RuntimeError(f"COOPS error: {r.text[:200]}")
    return pd.read_csv(io.StringIO(r.text))


def _normalize_tide(raw: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    if len(raw) == 0:
        return pd.DataFrame(columns=[f.name for f in TIDE_SCHEMA]), 0
    raw.columns = [c.strip() for c in raw.columns]
    if "Date Time" not in raw.columns or "Water Level" not in raw.columns:
        return pd.DataFrame(columns=[f.name for f in TIDE_SCHEMA]), 0
    out = pd.DataFrame()
    out["timestamp"] = pd.to_datetime(raw["Date Time"], utc=True, errors="coerce")
    out["water_level_m"] = pd.to_numeric(raw["Water Level"], errors="coerce").astype("float32")
    out["station_id"] = pd.Series([SF_STATION] * len(out)).astype("string")
    if "Sigma" in raw.columns:
        out["sigma"] = pd.to_numeric(raw["Sigma"], errors="coerce").astype("float32")
    else:
        out["sigma"] = pd.Series([np.nan] * len(out), dtype="float32")
    bad = out["timestamp"].isna() | out["water_level_m"].isna()
    skipped = int(bad.sum())
    out = out[~bad].copy()
    out = out.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    return out, skipped


def run_tide(reset: bool, stat: SourceStat) -> None:
    print("[tide] starting (SF station 9414290)")
    decades_done = {} if reset else _existing_decade_paths("tide")
    print(f"[tide] existing decades: {list(decades_done.keys())}")

    for decade_name, lo, hi in DECADES:
        if decade_name in decades_done:
            p = decades_done[decade_name]
            stat.decade_bytes[decade_name] = os.path.getsize(p)
            try:
                stat.decade_rows[decade_name] = len(pq.read_table(p))
            except Exception:
                stat.decade_rows[decade_name] = -1
            print(f"[tide] {decade_name}: SKIP ({stat.decade_rows[decade_name]:,} rows)")
            continue

        frames = []
        for year in range(lo, hi + 1):
            try:
                raw = _fetch_coops_year(year)
                stat.http_count += 1
                norm, skipped = _normalize_tide(raw)
                stat.rows_skipped += skipped
                if len(norm):
                    frames.append(norm)
                    stat.years_ok.append(year)
                    print(f"[tide]   {year}: {len(norm):,} rows ({skipped} skipped)")
                else:
                    stat.years_failed.append((year, "0 rows after normalize"))
                    print(f"[tide]   {year}: 0 rows")
            except Exception as e:
                stat.years_failed.append((year, str(e)[:200]))
                print(f"[tide]   {year}: ERROR {e}")
            time.sleep(1.0)

        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if len(df):
            df["timestamp"] = _coerce_dt_ns_utc(df["timestamp"])
            df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
            if stat.min_ts is None or df["timestamp"].min() < stat.min_ts:
                stat.min_ts = df["timestamp"].min()
            if stat.max_ts is None or df["timestamp"].max() > stat.max_ts:
                stat.max_ts = df["timestamp"].max()
            stat.gaps_over_7d.extend(_gaps_over(df["timestamp"], pd.Timedelta(days=7)))

        out = decade_path("tide", decade_name)
        size = _write_decade(df, TIDE_SCHEMA, out)
        stat.rows_total += len(df)
        stat.decade_rows[decade_name] = len(df)
        stat.decade_bytes[decade_name] = size
        print(f"[tide] {decade_name}: wrote {len(df):,} rows -> {out} ({size:,} bytes)")


# ── Report ──────────────────────────────────────────────────────

def render_report(stats: List[SourceStat], wall_seconds: float) -> str:
    lines = []
    lines.append("# BULK_REPORT_1973_2024 — geosolar archive bulk fetch")
    lines.append("")
    lines.append(f"_Run: {datetime.now(timezone.utc).isoformat(timespec='seconds')} · "
                 f"wall-clock {wall_seconds/60:.1f} min_")
    lines.append("")
    lines.append("Coverage: **1973-01-01 .. 2024-12-31**. 2025 data is in the pilot files "
                 "(`kp_2025.parquet`, `dst_2025.parquet`, `seismic_2025_M4plus.parquet`, "
                 "`tide_sf_2025_hourly.parquet`); merge at analysis time. Decade partitioning "
                 "uses fixed boundaries (1970s = 1973–1979 partial; 2020s = 2020–2024 partial; "
                 "all others full 10-year decades).")
    lines.append("")

    total_bytes = 0
    for s in stats:
        total_bytes += sum(s.decade_bytes.values())

    lines.append(f"## Footprint")
    lines.append("")
    lines.append(f"Total disk: **{total_bytes:,} bytes** ({total_bytes/1024/1024:.1f} MB) "
                 f"across the 24 decade Parquet files.")
    lines.append("")

    for s in stats:
        lines.append(f"## {s.name}")
        lines.append("")
        lines.append(f"- HTTP requests: **{s.http_count:,}**")
        lines.append(f"- years OK: **{len(set(s.years_ok))}** / {END_YEAR - START_YEAR + 1}")
        lines.append(f"- years failed: **{len(s.years_failed)}**")
        lines.append(f"- rows total: **{s.rows_total:,}**")
        lines.append(f"- rows skipped (malformed): {s.rows_skipped:,}")
        if s.min_ts is not None:
            lines.append(f"- date range: {s.min_ts}  →  {s.max_ts}")
        if "cutoffs" in s.extras:
            lines.append(f"- Dst cutoffs: {s.extras['cutoffs']}")
        lines.append("")
        lines.append("| decade | rows | bytes | path |")
        lines.append("|---|---:|---:|---|")
        for name, _lo, _hi in DECADES:
            r = s.decade_rows.get(name, 0)
            b = s.decade_bytes.get(name, 0)
            p = decade_path(s.name, name)
            relp = os.path.relpath(p, REPO_ROOT)
            lines.append(f"| {name} | {r:,} | {b:,} | `{relp}` |")
        lines.append("")
        if s.name == "seismic" and "mag_bins" in s.extras:
            lines.append("**Magnitude bins per decade:**")
            lines.append("")
            lines.append("| decade | M4.0-4.9 | M5.0-5.9 | M6.0-6.9 | M7.0+ |")
            lines.append("|---|---:|---:|---:|---:|")
            for name, _lo, _hi in DECADES:
                bins = s.extras["mag_bins"].get(name, {})
                lines.append(f"| {name} | {bins.get('M4.0-4.9', 0):,} | "
                             f"{bins.get('M5.0-5.9', 0):,} | "
                             f"{bins.get('M6.0-6.9', 0):,} | {bins.get('M7.0+', 0):,} |")
            lines.append("")
        if s.gaps_over_7d:
            lines.append(f"**Gaps > 7 days (first {min(5, len(s.gaps_over_7d))}):**")
            lines.append("")
            for prev, nxt, gap in s.gaps_over_7d[:5]:
                lines.append(f"- `{prev}`  →  `{nxt}`  ({gap})")
            lines.append("")
        if s.years_failed:
            lines.append(f"**Failed years ({len(s.years_failed)}):**")
            lines.append("")
            shown = s.years_failed[:20]
            for y, reason in shown:
                lines.append(f"- {y}: {reason}")
            if len(s.years_failed) > 20:
                lines.append(f"- … and {len(s.years_failed) - 20} more")
            lines.append("")

    # Degraded coverage summary
    lines.append("## Degraded coverage summary")
    lines.append("")
    any_degraded = False
    for s in stats:
        for name, _lo, _hi in DECADES:
            r = s.decade_rows.get(name, 0)
            expected = {"kp": 8 * 365 * (_hi - _lo + 1),
                        "dst": 24 * 365 * (_hi - _lo + 1),
                        "tide": 24 * 365 * (_hi - _lo + 1)}.get(s.name, 0)
            if expected and r < expected * 0.7:
                lines.append(f"- **{s.name} {name}**: {r:,} rows vs ~{expected:,} expected "
                             f"({r/expected*100:.0f}%)")
                any_degraded = True
    if not any_degraded:
        lines.append("None — all decades within tolerance for their nominal expected row counts.")
    lines.append("")

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true",
                    help="Re-fetch all decades, ignoring existing files")
    args = ap.parse_args()

    _ensure_dirs()

    t0 = time.time()
    print(f"[bulk] start {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"[bulk] coverage: {START_YEAR}-{END_YEAR}, decades = {[d[0] for d in DECADES]}")
    if args.reset:
        print("[bulk] --reset: existing decade files will be overwritten")

    stats: List[SourceStat] = []

    s_kp = SourceStat(name="kp")
    run_kp(args.reset, s_kp)
    stats.append(s_kp)

    s_dst = SourceStat(name="dst")
    run_dst(args.reset, s_dst)
    stats.append(s_dst)

    s_seis = SourceStat(name="seismic")
    run_seismic(args.reset, s_seis)
    stats.append(s_seis)

    s_tide = SourceStat(name="tide")
    run_tide(args.reset, s_tide)
    stats.append(s_tide)

    elapsed = time.time() - t0
    print(f"\n[bulk] done in {elapsed/60:.1f} min")

    report = render_report(stats, elapsed)
    with open(REPORT_OUT, "w") as f:
        f.write(report)
    print(f"[bulk] report -> {REPORT_OUT}")
    print()
    print(report)


if __name__ == "__main__":
    main()
