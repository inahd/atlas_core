"""
PILOT — geosolar archive validation run for calendar year 2025.

This is a one-year bounded pilot used to validate the fetch pipeline end-to-end
before committing to a multi-decade bulk pull. Four sources, four canonical
schemas, four Parquet files, one Markdown validation report.

Sources fetched here:
  Kp       — GFZ Potsdam definitive Kp_def2025.wdc
  Dst      — Kyoto WDC monthly files (provisional Jan–Jun 2025 + realtime Jul–Dec 2025)
  Seismic  — USGS ANSS ComCat, 2025 M ≥ 4.0
  Tide     — NOAA CO-OPS station 9414290 (San Francisco), hourly_height 2025

The full multi-decade run will be a separate script invocation; this pilot
must succeed cleanly before that script is written.

Run:
    /home/inahd/atlas_core/.venv-archive/bin/python -m npu_engine.jobs.geosolar_archive_pilot

Outputs:
    datasets/geosolar/archive/kp/kp_2025.parquet
    datasets/geosolar/archive/dst/dst_2025.parquet
    datasets/geosolar/archive/seismic/seismic_2025_M4plus.parquet
    datasets/geosolar/archive/tide/tide_sf_2025_hourly.parquet
    datasets/geosolar/archive/PILOT_REPORT_2025.md
"""
from __future__ import annotations

import io
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ARCHIVE_DIR = os.path.join(REPO_ROOT, "datasets", "geosolar", "archive")

KP_OUT      = os.path.join(ARCHIVE_DIR, "kp",      "kp_2025.parquet")
DST_OUT     = os.path.join(ARCHIVE_DIR, "dst",     "dst_2025.parquet")
SEIS_OUT    = os.path.join(ARCHIVE_DIR, "seismic", "seismic_2025_M4plus.parquet")
TIDE_OUT    = os.path.join(ARCHIVE_DIR, "tide",    "tide_sf_2025_hourly.parquet")
REPORT_OUT  = os.path.join(ARCHIVE_DIR, "PILOT_REPORT_2025.md")

UA = "AtlasCore-pilot/0.1 (research; inahd108@proton.me)"
HEADERS = {"User-Agent": UA}


# ── Schemas ─────────────────────────────────────────────────────────────

KP_SCHEMA = pa.schema([
    ("timestamp", pa.timestamp("ns", tz="UTC")),
    ("kp", pa.float32()),
    ("ap", pa.float32()),
])

DST_SCHEMA = pa.schema([
    ("timestamp", pa.timestamp("ns", tz="UTC")),
    ("dst_nT", pa.float32()),
])

SEIS_SCHEMA = pa.schema([
    ("timestamp", pa.timestamp("ns", tz="UTC")),
    ("latitude", pa.float64()),
    ("longitude", pa.float64()),
    ("depth_km", pa.float32()),
    ("magnitude", pa.float32()),
    ("magType", pa.string()),
    ("place", pa.string()),
    ("event_id", pa.string()),
])

TIDE_SCHEMA = pa.schema([
    ("timestamp", pa.timestamp("ns", tz="UTC")),
    ("water_level_m", pa.float32()),
    ("station_id", pa.string()),
    ("sigma", pa.float32()),
])


# ── Per-source result bookkeeping ───────────────────────────────────────

@dataclass
class FetchResult:
    name: str
    out_path: str
    http_count: int = 0
    rows_fetched: int = 0
    rows_skipped: int = 0
    min_ts: Optional[pd.Timestamp] = None
    max_ts: Optional[pd.Timestamp] = None
    gaps_over_1day: List[tuple] = field(default_factory=list)
    file_size_bytes: int = 0
    sample_rows: Optional[pd.DataFrame] = None
    error: Optional[str] = None
    extras: dict = field(default_factory=dict)


def _write_parquet(df: pd.DataFrame, schema: pa.Schema, out_path: str) -> int:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if len(df) == 0:
        # Empty file with schema preserved.
        empty_table = pa.Table.from_pylist([], schema=schema)
        pq.write_table(empty_table, out_path)
    else:
        table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
        pq.write_table(table, out_path)
    return os.path.getsize(out_path)


def _gaps(timestamps: pd.Series, threshold: pd.Timedelta) -> List[tuple]:
    if len(timestamps) < 2:
        return []
    s = timestamps.sort_values().reset_index(drop=True)
    diffs = s.diff()
    out = []
    for i, d in enumerate(diffs):
        if pd.notna(d) and d > threshold:
            out.append((str(s.iloc[i - 1]), str(s.iloc[i]), str(d)))
    return out


# ── (1) Kp — GFZ Potsdam ────────────────────────────────────────────────

def fetch_kp() -> FetchResult:
    res = FetchResult(name="kp", out_path=KP_OUT)
    url = "https://datapub.gfz-potsdam.de/download/10.5880.Kp.0001/Kp_definitive/Kp_def2025.wdc"
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        res.http_count += 1
        r.raise_for_status()
        text = r.text
    except Exception as e:
        res.error = f"GFZ Kp fetch failed: {e}"
        print(f"  [kp] ERROR {res.error}")
        size = _write_parquet(pd.DataFrame(columns=[f.name for f in KP_SCHEMA]), KP_SCHEMA, KP_OUT)
        res.file_size_bytes = size
        return res

    rows = []
    skipped = 0
    lines = text.splitlines()

    # GFZ Kp_def<YYYY>.wdc fixed-width format. One line per UTC day, 62 chars.
    # Field widths (1-indexed inclusive cols):
    #   1-2   yy   (right-justified, space-padded)
    #   3-4   mm   (right-justified, space-padded)
    #   5-6   dd   (right-justified, space-padded)
    #   7-10  Bartels solar rotation #
    #  11-12  Bartels day
    #  13-28  8 × Kp×10  (2 chars each, e.g. "27" = Kp 2.7)
    #  29-31  daily Kp sum × 10
    #  32-55  8 × ap     (3 chars each, right-justified)
    #  56-58  daily Ap
    #  59-62  Cp
    # We extract timestamps + 8 Kp + 8 ap for each day.
    KP_HOUR_STARTS = [0, 3, 6, 9, 12, 15, 18, 21]

    candidate_lines = [ln for ln in lines if len(ln) >= 58 and ln[0:2].strip().isdigit()]
    total = len(candidate_lines)
    progress_step = max(1, total // 10)
    processed = 0

    for ln in candidate_lines:
        try:
            yy = int(ln[0:2])
            month_s = ln[2:4].strip()
            day_s = ln[4:6].strip()
            if not month_s or not day_s:
                skipped += 1
                continue
            year = 2000 + yy if yy < 70 else 1900 + yy
            month = int(month_s)
            day = int(day_s)
            day_dt = datetime(year, month, day, tzinfo=timezone.utc)

            kp_field = ln[12:28]   # 16 chars = 8 × 2
            ap_field = ln[31:55]   # 24 chars = 8 × 3

            for i, hr in enumerate(KP_HOUR_STARTS):
                kp_raw = kp_field[i * 2:(i + 1) * 2].strip()
                ap_raw = ap_field[i * 3:(i + 1) * 3].strip()
                if not kp_raw or not ap_raw:
                    skipped += 1
                    continue
                try:
                    kp_val = int(kp_raw) / 10.0  # stored as Kp × 10
                    ap_val = float(ap_raw)
                except ValueError:
                    skipped += 1
                    continue
                ts = day_dt + timedelta(hours=hr)
                rows.append({"timestamp": ts, "kp": kp_val, "ap": ap_val})
            processed += 1
            if total > 100 and processed % progress_step == 0:
                pct = int(processed / total * 100)
                print(f"  [kp] parsed {processed}/{total} days ({pct}%)")
        except Exception:
            skipped += 1
            continue

    df = pd.DataFrame(rows)
    if len(df):
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df["kp"] = df["kp"].astype("float32")
        df["ap"] = df["ap"].astype("float32")
        df = df.sort_values("timestamp").reset_index(drop=True)
        res.min_ts = df["timestamp"].min()
        res.max_ts = df["timestamp"].max()
        res.gaps_over_1day = _gaps(df["timestamp"], pd.Timedelta(days=1))[:5]
        res.sample_rows = df.head(5).copy()

    res.rows_fetched = len(df)
    res.rows_skipped = skipped
    res.file_size_bytes = _write_parquet(df, KP_SCHEMA, KP_OUT)
    return res


# ── (2) Dst — Kyoto WDC monthly files ───────────────────────────────────

def _parse_dst_file(text: str) -> tuple[list[dict], int]:
    """Parse one monthly Kyoto WDC Dst file (e.g., dst2501.for.request).

    Each line: chars 0..19 are the header (DST + yymm + * + dd + status code +
    flags + base value). Chars 20..115 are 24 hourly Dst values, 4 chars each.
    Chars 116..119 are the daily mean.
    """
    rows = []
    skipped = 0
    for ln in text.splitlines():
        if not ln.startswith("DST"):
            continue
        if len(ln) < 116:
            skipped += 1
            continue
        try:
            yy = int(ln[3:5])
            month = int(ln[5:7])
            day = int(ln[8:10])
            year = 2000 + yy if yy < 70 else 1900 + yy
            day_dt = datetime(year, month, day, tzinfo=timezone.utc)
            for hr in range(24):
                start = 20 + hr * 4
                v_raw = ln[start:start + 4].strip()
                if not v_raw or v_raw in ("9999", "999"):
                    skipped += 1
                    continue
                try:
                    val = float(v_raw)
                except ValueError:
                    skipped += 1
                    continue
                # Hourly Dst values are end-of-hour averages stamped at HH:30 UT
                # by convention, but the standard archive convention stores
                # them at the start of the hour. We use start-of-hour to keep
                # joins simple.
                ts = day_dt + timedelta(hours=hr)
                rows.append({"timestamp": ts, "dst_nT": val})
        except Exception:
            skipped += 1
            continue
    return rows, skipped


def fetch_dst() -> FetchResult:
    res = FetchResult(name="dst", out_path=DST_OUT)

    months = [(2025, m) for m in range(1, 13)]
    # Provisional covers 2025/01..2025/06 per the index page; realtime covers 2025/07+
    PROVISIONAL_BASE = "https://wdc.kugi.kyoto-u.ac.jp/dst_provisional"
    REALTIME_BASE    = "https://wdc.kugi.kyoto-u.ac.jp/dst_realtime"

    rows = []
    skipped_total = 0
    for year, month in months:
        yymm = f"{year % 100:02d}{month:02d}"
        base = PROVISIONAL_BASE if month <= 6 else REALTIME_BASE
        url = f"{base}/{year}{month:02d}/dst{yymm}.for.request"
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
            res.http_count += 1
            if r.status_code != 200:
                print(f"  [dst] {yymm} HTTP {r.status_code} — skipping month")
                continue
            text = r.text
            month_rows, sk = _parse_dst_file(text)
            rows.extend(month_rows)
            skipped_total += sk
            print(f"  [dst] {yymm}: {len(month_rows)} rows, {sk} skipped")
        except Exception as e:
            print(f"  [dst] {yymm} ERROR: {e}")
        time.sleep(0.5)  # polite

    df = pd.DataFrame(rows)
    if len(df):
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df["dst_nT"] = df["dst_nT"].astype("float32")
        df = df.sort_values("timestamp").reset_index(drop=True)
        res.min_ts = df["timestamp"].min()
        res.max_ts = df["timestamp"].max()
        res.gaps_over_1day = _gaps(df["timestamp"], pd.Timedelta(days=1))[:5]
        res.sample_rows = df.head(5).copy()

    res.rows_fetched = len(df)
    res.rows_skipped = skipped_total
    res.file_size_bytes = _write_parquet(df, DST_SCHEMA, DST_OUT)
    return res


# ── (3) Seismic — USGS ComCat ───────────────────────────────────────────

def _fetch_usgs_chunk(start: str, end: str) -> tuple[pd.DataFrame, int]:
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "csv",
        "starttime": start,
        "endtime": end,
        "minmagnitude": 4.0,
        "orderby": "time-asc",
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=120)
    if r.status_code == 400:
        # Likely too many results; signal caller to paginate
        return pd.DataFrame(), 1
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    return df, 1


def fetch_seismic() -> FetchResult:
    res = FetchResult(name="seismic", out_path=SEIS_OUT)

    # Try whole year first; paginate quarterly if needed.
    frames: list[pd.DataFrame] = []
    skipped = 0
    try:
        df_year, _ = _fetch_usgs_chunk("2025-01-01", "2025-12-31T23:59:59")
        res.http_count += 1
        time.sleep(1.0)
        if len(df_year) >= 19000 or len(df_year) == 0:
            print(f"  [seismic] single-shot returned {len(df_year)} rows — paginating quarterly")
            frames = []
            quarters = [
                ("2025-01-01", "2025-03-31T23:59:59"),
                ("2025-04-01", "2025-06-30T23:59:59"),
                ("2025-07-01", "2025-09-30T23:59:59"),
                ("2025-10-01", "2025-12-31T23:59:59"),
            ]
            for s, e in quarters:
                dfq, _ = _fetch_usgs_chunk(s, e)
                res.http_count += 1
                print(f"  [seismic] {s}..{e}: {len(dfq)} rows")
                frames.append(dfq)
                time.sleep(1.0)
        else:
            frames = [df_year]
    except Exception as e:
        res.error = f"USGS fetch failed: {e}"
        print(f"  [seismic] ERROR {res.error}")
        size = _write_parquet(pd.DataFrame(columns=[f.name for f in SEIS_SCHEMA]),
                              SEIS_SCHEMA, SEIS_OUT)
        res.file_size_bytes = size
        return res

    raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if len(raw) == 0:
        res.rows_fetched = 0
        res.file_size_bytes = _write_parquet(
            pd.DataFrame(columns=[f.name for f in SEIS_SCHEMA]), SEIS_SCHEMA, SEIS_OUT
        )
        return res

    # Map to canonical schema
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
    out = out[~bad].copy().reset_index(drop=True)
    out = out.drop_duplicates(subset=["event_id"]).sort_values("timestamp").reset_index(drop=True)

    # Magnitude bin counts
    bins = {
        "M4.0-4.9": int(((out["magnitude"] >= 4.0) & (out["magnitude"] < 5.0)).sum()),
        "M5.0-5.9": int(((out["magnitude"] >= 5.0) & (out["magnitude"] < 6.0)).sum()),
        "M6.0-6.9": int(((out["magnitude"] >= 6.0) & (out["magnitude"] < 7.0)).sum()),
        "M7.0+":    int((out["magnitude"] >= 7.0).sum()),
    }
    res.extras["magnitude_bins"] = bins

    res.min_ts = out["timestamp"].min()
    res.max_ts = out["timestamp"].max()
    res.gaps_over_1day = _gaps(out["timestamp"], pd.Timedelta(days=1))[:5]
    res.sample_rows = out.head(5).copy()
    res.rows_fetched = len(out)
    res.rows_skipped = skipped
    res.file_size_bytes = _write_parquet(out, SEIS_SCHEMA, SEIS_OUT)
    return res


# ── (4) Tide — NOAA CO-OPS ──────────────────────────────────────────────

def _fetch_coops(begin_yyyymmdd: str, end_yyyymmdd: str) -> pd.DataFrame:
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": "hourly_height",
        "application": "AtlasCore",
        "begin_date": begin_yyyymmdd,
        "end_date": end_yyyymmdd,
        "datum": "MLLW",
        "station": "9414290",
        "time_zone": "GMT",
        "units": "metric",
        "format": "csv",
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    text = r.text
    # CO-OPS error responses come back as plain text starting with "Error: "
    if text.lstrip().lower().startswith("error"):
        raise RuntimeError(f"COOPS error body: {text[:200]}")
    df = pd.read_csv(io.StringIO(text))
    return df


def fetch_tide() -> FetchResult:
    res = FetchResult(name="tide", out_path=TIDE_OUT)
    rows_frames: list[pd.DataFrame] = []
    skipped = 0
    try:
        df = _fetch_coops("20250101", "20251231")
        res.http_count += 1
        rows_frames.append(df)
        time.sleep(1.0)
    except Exception as e:
        print(f"  [tide] single-year fetch failed ({e}); paginating monthly")
        rows_frames = []
        months = [(2025, m) for m in range(1, 13)]
        for year, month in months:
            # last day of month
            if month == 12:
                last = 31
            else:
                last = (datetime(year, month + 1, 1) - timedelta(days=1)).day
            begin = f"{year}{month:02d}01"
            end = f"{year}{month:02d}{last:02d}"
            try:
                dfm = _fetch_coops(begin, end)
                res.http_count += 1
                rows_frames.append(dfm)
                print(f"  [tide] {begin}-{end}: {len(dfm)} rows")
            except Exception as e2:
                print(f"  [tide] {begin}-{end} ERROR: {e2}")
            time.sleep(1.0)

    if not rows_frames or all(len(f) == 0 for f in rows_frames):
        res.error = "no tide rows fetched"
        print(f"  [tide] ERROR {res.error}")
        size = _write_parquet(pd.DataFrame(columns=[f.name for f in TIDE_SCHEMA]),
                              TIDE_SCHEMA, TIDE_OUT)
        res.file_size_bytes = size
        return res

    raw = pd.concat(rows_frames, ignore_index=True)
    raw.columns = [c.strip() for c in raw.columns]

    # Locate columns. CO-OPS hourly_height returns:
    #   "Date Time", "Water Level", "Sigma", "I", "L"
    if "Date Time" not in raw.columns or "Water Level" not in raw.columns:
        res.error = f"unexpected tide columns: {list(raw.columns)}"
        print(f"  [tide] ERROR {res.error}")
        size = _write_parquet(pd.DataFrame(columns=[f.name for f in TIDE_SCHEMA]),
                              TIDE_SCHEMA, TIDE_OUT)
        res.file_size_bytes = size
        return res

    out = pd.DataFrame()
    out["timestamp"] = pd.to_datetime(raw["Date Time"], utc=True, errors="coerce")
    out["water_level_m"] = pd.to_numeric(raw["Water Level"], errors="coerce").astype("float32")
    out["station_id"] = "9414290"
    out["station_id"] = out["station_id"].astype("string")
    if "Sigma" in raw.columns:
        out["sigma"] = pd.to_numeric(raw["Sigma"], errors="coerce").astype("float32")
    else:
        out["sigma"] = pd.Series([float("nan")] * len(out), dtype="float32")

    bad = out["timestamp"].isna() | out["water_level_m"].isna()
    skipped = int(bad.sum())
    out = out[~bad].copy()
    out = out.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    res.min_ts = out["timestamp"].min()
    res.max_ts = out["timestamp"].max()
    res.gaps_over_1day = _gaps(out["timestamp"], pd.Timedelta(days=1))[:5]
    res.sample_rows = out.head(5).copy()
    res.rows_fetched = len(out)
    res.rows_skipped = skipped
    res.file_size_bytes = _write_parquet(out, TIDE_SCHEMA, TIDE_OUT)
    return res


# ── Round-trip verification ─────────────────────────────────────────────

def _readback_sample(path: str, n: int = 5) -> Optional[pd.DataFrame]:
    try:
        return pq.read_table(path).to_pandas().head(n)
    except Exception as e:
        print(f"  [readback] {path} failed: {e}")
        return None


# ── Report ──────────────────────────────────────────────────────────────

def render_report(results: List[FetchResult]) -> str:
    lines = []
    lines.append("# PILOT_REPORT_2025 — geosolar archive validation")
    lines.append("")
    lines.append(f"Run timestamp: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append("")
    for r in results:
        lines.append(f"## {r.name}")
        lines.append("")
        if r.error:
            lines.append(f"**ERROR:** {r.error}")
            lines.append("")
        lines.append(f"- output: `{os.path.relpath(r.out_path, REPO_ROOT)}`")
        lines.append(f"- file size: {r.file_size_bytes:,} bytes")
        lines.append(f"- HTTP requests: {r.http_count}")
        lines.append(f"- rows fetched: {r.rows_fetched:,}")
        lines.append(f"- rows skipped (malformed): {r.rows_skipped:,}")
        if r.min_ts is not None and r.max_ts is not None:
            lines.append(f"- date range: {r.min_ts}  →  {r.max_ts}")
        if r.gaps_over_1day:
            lines.append(f"- gaps > 1 day (first {len(r.gaps_over_1day)}):")
            for prev, nxt, gap in r.gaps_over_1day:
                lines.append(f"    - {prev}  →  {nxt}  ({gap})")
        else:
            lines.append("- gaps > 1 day: none")
        if "magnitude_bins" in r.extras:
            lines.append("- magnitude bin counts:")
            for k, v in r.extras["magnitude_bins"].items():
                lines.append(f"    - {k}: {v:,}")
        sample = _readback_sample(r.out_path, 5)
        if sample is not None and len(sample):
            lines.append("")
            lines.append("**Sample rows (round-trip read from Parquet):**")
            lines.append("")
            lines.append("```")
            lines.append(sample.to_string(index=False))
            lines.append("```")
        elif r.rows_fetched == 0:
            lines.append("")
            lines.append("**Sample rows: none — empty file with schema preserved.**")
        lines.append("")
    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────

def main():
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    print(f"[pilot] writing into {ARCHIVE_DIR}")
    results: List[FetchResult] = []

    print("\n[pilot] (1/4) Kp")
    r = fetch_kp()
    results.append(r)
    if r.rows_fetched == 0 and r.error:
        print(f"[pilot] ABORT after kp — {r.error}")
        with open(REPORT_OUT, "w") as f:
            f.write(render_report(results))
        return 1

    print("\n[pilot] (2/4) Dst")
    r = fetch_dst()
    results.append(r)
    if r.rows_fetched == 0 and r.error:
        print(f"[pilot] ABORT after dst — {r.error}")
        with open(REPORT_OUT, "w") as f:
            f.write(render_report(results))
        return 1

    print("\n[pilot] (3/4) Seismic")
    r = fetch_seismic()
    results.append(r)
    if r.rows_fetched == 0 and r.error:
        print(f"[pilot] ABORT after seismic — {r.error}")
        with open(REPORT_OUT, "w") as f:
            f.write(render_report(results))
        return 1

    print("\n[pilot] (4/4) Tide")
    r = fetch_tide()
    results.append(r)

    report = render_report(results)
    with open(REPORT_OUT, "w") as f:
        f.write(report)
    print("\n" + "=" * 72)
    print(report)
    print("=" * 72)
    print(f"\n[pilot] report written to {REPORT_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
