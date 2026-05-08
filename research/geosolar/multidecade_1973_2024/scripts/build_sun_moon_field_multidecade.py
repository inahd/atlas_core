"""
Build sun_moon_amplitude scalar at the Gainesville lagna for the multi-decade
panchanga grid (1973-01-01 .. 2024-12-31, 10-min cadence).

Reduction (locked, identical to the 2025 pilot at
research/geosolar/pilot_2025/scripts/build_sun_moon_field.py):

    sun_long, moon_long, lagna_long = compute_chart(t, 29.65, -82.34)
    A_k = compute_pair_interference(sun_long, moon_long, lagna_long, k)
    sun_moon_amplitude = mean over k ∈ {1,2,3,4,6,7,12} of |A_k|

Per-decade input/output to bound peak memory:
    in:  datasets/panchanga/grid_10min_{decade}s.parquet  (timestamp column)
    out: research/geosolar/multidecade_1973_2024/sun_moon_field_{decade}s.parquet
         columns: timestamp, sun_long, moon_long, lagna_long, sun_moon_amplitude

A final concatenation pass writes
    research/geosolar/multidecade_1973_2024/sun_moon_field_1973_2024.parquet
"""
from __future__ import annotations

import os
import sys
import time
from datetime import timezone
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = "/home/inahd/atlas_core"
sys.path.insert(0, ROOT)

GRID_DIR = os.path.join(ROOT, "datasets/panchanga")
OUT_DIR = os.path.join(ROOT, "research/geosolar/multidecade_1973_2024")

DECADES = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]

LAT, LON = 29.65, -82.34
K_VALUES = [1, 2, 3, 4, 6, 7, 12]


def _worker(ts_chunk):
    from npu_engine.jyotisha_engine import compute_chart, compute_pair_interference
    n = len(ts_chunk)
    sun = np.empty(n, dtype=np.float64)
    moon = np.empty(n, dtype=np.float64)
    lagna = np.empty(n, dtype=np.float64)
    amp = np.empty(n, dtype=np.float64)
    for i, ts in enumerate(ts_chunk):
        dt = ts.to_pydatetime()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ch = compute_chart(dt, LAT, LON)
        sl = float(ch["grahas"]["Sun"]["deg_absolute"])
        ml = float(ch["grahas"]["Moon"]["deg_absolute"])
        lg = float(ch["ascendant"]["deg_absolute"])
        sun[i] = sl
        moon[i] = ml
        lagna[i] = lg
        s = 0.0
        for k in K_VALUES:
            a = compute_pair_interference(sl, ml, lg, k)
            s += abs(a)
        amp[i] = s / len(K_VALUES)
    return sun, moon, lagna, amp


def _build_decade(label):
    in_path = os.path.join(GRID_DIR, f"grid_10min_{label}.parquet")
    out_path = os.path.join(OUT_DIR, f"sun_moon_field_{label}.parquet")
    if os.path.exists(out_path):
        existing = pd.read_parquet(out_path, columns=["timestamp"])
        print(f"[{label}] EXISTS: {len(existing):,} rows → skip")
        return
    if not os.path.exists(in_path):
        print(f"[{label}] MISSING grid {in_path} → skip")
        return

    grid = pd.read_parquet(in_path, columns=["timestamp"])
    ts = grid["timestamp"]
    if ts.dt.tz is None:
        ts = ts.dt.tz_localize("UTC")
    ts = ts.dt.tz_convert("UTC")
    n = len(ts)
    n_workers = max(1, min(12, (os.cpu_count() or 4) - 2))
    chunk_size = max(1, n // (n_workers * 8))
    chunks = [ts.iloc[i:i + chunk_size].tolist() for i in range(0, n, chunk_size)]
    print(f"[{label}] n={n:,}  workers={n_workers}  chunks={len(chunks)}  chunk_size~{chunk_size}")

    sun_out = np.empty(n, dtype=np.float32)
    moon_out = np.empty(n, dtype=np.float32)
    lagna_out = np.empty(n, dtype=np.float32)
    amp_out = np.empty(n, dtype=np.float32)
    cursor = 0
    t0 = time.time()
    with Pool(processes=n_workers) as pool:
        for j, (s, m, l, a) in enumerate(pool.imap(_worker, chunks)):
            k = len(s)
            sun_out[cursor:cursor + k] = s.astype(np.float32)
            moon_out[cursor:cursor + k] = m.astype(np.float32)
            lagna_out[cursor:cursor + k] = l.astype(np.float32)
            amp_out[cursor:cursor + k] = a.astype(np.float32)
            cursor += k
            if (j + 1) % max(1, len(chunks) // 20) == 0 or j + 1 == len(chunks):
                pct = 100.0 * cursor / n
                elapsed = time.time() - t0
                eta = (elapsed / cursor * (n - cursor)) if cursor > 0 else 0
                print(f"  [{label}] {cursor:,}/{n:,} ({pct:.1f}%)  elapsed {elapsed:.1f}s  eta {eta:.1f}s")
    assert cursor == n

    df = pd.DataFrame({
        "timestamp": pd.to_datetime(ts.values, utc=True),
        "sun_long": sun_out,
        "moon_long": moon_out,
        "lagna_long": lagna_out,
        "sun_moon_amplitude": amp_out,
    })
    df["timestamp"] = df["timestamp"].astype("datetime64[ns, UTC]")
    df.to_parquet(out_path, index=False)
    print(f"  [{label}] wrote {out_path}  rows={len(df):,}  wall={time.time()-t0:.1f}s")


def _concat_all():
    out_full = os.path.join(OUT_DIR, "sun_moon_field_1973_2024.parquet")
    if os.path.exists(out_full):
        existing = pd.read_parquet(out_full, columns=["timestamp"])
        print(f"[concat] EXISTS: {len(existing):,} rows → skip")
        return
    parts = []
    for label in DECADES:
        p = os.path.join(OUT_DIR, f"sun_moon_field_{label}.parquet")
        if os.path.exists(p):
            parts.append(pd.read_parquet(p))
    if not parts:
        print("[concat] no parts found → skip")
        return
    df = pd.concat(parts, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
    df.to_parquet(out_full, index=False)
    print(f"[concat] wrote {out_full}  rows={len(df):,}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    for label in DECADES:
        _build_decade(label)
    _concat_all()
    print(f"\nTOTAL sun_moon_field wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
