"""
EXPLORATORY: Sun-Moon raw-amplitude wave-field at the lagna, every 10 min in 2025.

Why this scalar (per the follow-up brief):
  - The prior zodiacal-mean wave_field_mean returned a clean null. Diagnostic
    evidence pointed to per-k min-max normalization compressing variance below
    detectable levels (std=0.032 across the year).
  - This drops the normalization. For each timestamp we compute the raw
    Sun-Moon two-source amplitude at the lagna (rising point at Gainesville),
    averaged over k ∈ {1, 2, 3, 4, 6, 7, 12}. Range [0, 2].

Per spec:
  - sun_long, moon_long, lagna_long via compute_chart (Lahiri sidereal,
    lat=29.65, lon=-82.34).
  - For each k: A_k = cos(k·(lagna − sun_long)) + cos(k·(lagna − moon_long))
    (this matches compute_pair_interference from jyotisha_engine.py).
  - sun_moon_amplitude = mean over k of |A_k|.

Output: research/geosolar/pilot_2025/sun_moon_field_2025.parquet
  columns: timestamp, sun_long, moon_long, lagna_long, sun_moon_amplitude
"""
from __future__ import annotations

import math
import os
import sys
import time
from datetime import datetime, timezone
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = "/home/inahd/atlas_core"
sys.path.insert(0, ROOT)

GRID_PATH = os.path.join(ROOT, "datasets/panchanga/grid_10min_2025.parquet")
OUT_PATH = os.path.join(ROOT, "research/geosolar/pilot_2025/sun_moon_field_2025.parquet")

LAT, LON = 29.65, -82.34
K_VALUES = [1, 2, 3, 4, 6, 7, 12]


def _worker(ts_chunk: list[pd.Timestamp]):
    """Per-chunk: returns (sun, moon, lagna, amp) numpy arrays."""
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
        # Raw Sun-Moon amplitude at lagna: mean over k of |A_k|.
        s = 0.0
        for k in K_VALUES:
            a = compute_pair_interference(sl, ml, lg, k)
            s += abs(a)
        amp[i] = s / len(K_VALUES)
    return sun, moon, lagna, amp


def main():
    t0 = time.time()
    grid = pd.read_parquet(GRID_PATH, columns=["timestamp"])
    ts = grid["timestamp"]
    if ts.dt.tz is None:
        ts = ts.dt.tz_localize("UTC")
    ts = ts.dt.tz_convert("UTC")
    n = len(ts)
    print(f"loaded grid: {n} timestamps")

    n_workers = max(1, min(12, os.cpu_count() - 2))
    chunk_size = max(1, n // (n_workers * 8))
    chunks = [ts.iloc[i:i + chunk_size].tolist() for i in range(0, n, chunk_size)]
    print(f"workers={n_workers} chunks={len(chunks)} chunk_size~{chunk_size}")

    sun_out = np.empty(n, dtype=np.float32)
    moon_out = np.empty(n, dtype=np.float32)
    lagna_out = np.empty(n, dtype=np.float32)
    amp_out = np.empty(n, dtype=np.float32)
    cursor = 0
    with Pool(processes=n_workers) as pool:
        for j, (s, m, l, a) in enumerate(pool.imap(_worker, chunks)):
            k = len(s)
            sun_out[cursor:cursor + k] = s.astype(np.float32)
            moon_out[cursor:cursor + k] = m.astype(np.float32)
            lagna_out[cursor:cursor + k] = l.astype(np.float32)
            amp_out[cursor:cursor + k] = a.astype(np.float32)
            cursor += k
            if (j + 1) % max(1, len(chunks) // 20) == 0:
                pct = 100.0 * cursor / n
                print(f"  progress: {cursor}/{n} ({pct:.1f}%)  elapsed {time.time() - t0:.1f}s")
    assert cursor == n

    df = pd.DataFrame({
        "timestamp": pd.to_datetime(ts.values, utc=True),
        "sun_long": sun_out,
        "moon_long": moon_out,
        "lagna_long": lagna_out,
        "sun_moon_amplitude": amp_out,
    })
    df["timestamp"] = df["timestamp"].astype("datetime64[ns, UTC]")
    df.to_parquet(OUT_PATH, index=False)
    print(f"wrote {OUT_PATH}: {len(df)} rows")

    # ── sanity ─────────────────────────────────────────────
    s = df["sun_moon_amplitude"]
    in_range = bool((s >= 0).all() and (s <= 2).all())
    print()
    print("=== sun_moon_amplitude distribution ===")
    print(f"  n           = {len(s)}")
    print(f"  n_nan       = {int(s.isna().sum())}")
    print(f"  min         = {float(s.min()):.6f}")
    print(f"  p25         = {float(s.quantile(0.25)):.6f}")
    print(f"  p50 (med)   = {float(s.quantile(0.50)):.6f}")
    print(f"  mean        = {float(s.mean()):.6f}")
    print(f"  p75         = {float(s.quantile(0.75)):.6f}")
    print(f"  max         = {float(s.max()):.6f}")
    print(f"  std         = {float(s.std()):.6f}")
    print(f"  in_[0,2]    = {in_range}")
    print(f"  std vs prior 0.0325: ratio = {float(s.std()) / 0.0325:.2f}x")

    # Stop-gate per spec: if std < 0.05, lagna-coupling didn't help; report and stop.
    if float(s.std()) < 0.05:
        print()
        print("[STOP-GATE] std < 0.05 — lagna-coupling did not unlock variance.")
        print("            The exploratory test will not be run on this scalar.")
    else:
        print()
        print("[OK] std ≥ 0.05; proceed to W1'-W4' battery.")
    print(f"total wall: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
